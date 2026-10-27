"""Official Meta Graph API publishing for Instagram (carousel) and Facebook Page (multi-photo)."""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT/'data'/'publish_state.json'
GRAPH = 'https://graph.facebook.com/v26.0'


def state_save(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(STATE_FILE)


def base_url(config):
    url = config.get('site_base_url', '').strip()
    if url:
        return url.rstrip('/')
    repository = os.getenv('GITHUB_REPOSITORY','')
    if '/' not in repository:
        raise RuntimeError('Indique site_base_url dans config.json (ex. https://nom.github.io/depot)')
    owner, repo = repository.split('/',1)
    return f'https://{owner}.github.io/{repo}'


def meta(method, path, token, **form):
    # Never print API tokens in logs.
    url = f'{GRAPH}/{path.lstrip("/")}'
    payload = {'access_token': token, **form}
    try:
        response = requests.request(method, url, data=payload if method=='POST' else None,
                                    params=payload if method=='GET' else None, timeout=35)
    except requests.RequestException as exc:
        raise RuntimeError(f'Réseau Meta indisponible ({type(exc).__name__}); vérifier Actions et relancer.') from None
    try:
        body = response.json()
    except ValueError:
        raise RuntimeError(f'Erreur Meta HTTP {response.status_code}: réponse illisible')
    if not response.ok or 'error' in body:
        err = body.get('error', {})
        msg = str(err.get('message','erreur inconnue')).replace(token, '[SECRET]')
        raise RuntimeError(f'Erreur Meta {response.status_code}, code {err.get("code","?")}: {msg}')
    return body


def wait_container(id, token, attempts=16):
    for i in range(attempts):
        state = meta('GET', id, token, fields='status_code').get('status_code')
        if state in ('FINISHED', 'PUBLISHED'):
            return
        if state in ('EXPIRED', 'ERROR'):
            raise RuntimeError(f'Conteneur Instagram en échec: {state}')
        if i < attempts-1:
            time.sleep(5)
    raise RuntimeError('Conteneur Instagram non prêt; relancer plus tard après vérification.')


def verify_public_images(urls):
    for url in urls:
        response = requests.get(url, timeout=25, stream=True, allow_redirects=True)
        try:
            if response.status_code != 200:
                raise RuntimeError(f'Image indisponible (HTTP {response.status_code}) : {url}')
            ctype = response.headers.get('content-type', '')
            if 'image/jpeg' not in ctype and 'image/jpg' not in ctype:
                raise RuntimeError(f'URL ne retourne pas un JPEG ({ctype}) : {url}')
        finally:
            response.close()


def instagram_publish(ig_id, token, images, caption):
    children = []
    for url in images:
        result = meta('POST', f'{ig_id}/media', token, image_url=url, is_carousel_item='true')
        children.append(result['id'])
    parent = meta('POST', f'{ig_id}/media', token, media_type='CAROUSEL',
                  children=','.join(children), caption=caption)['id']
    wait_container(parent, token)
    result = meta('POST', f'{ig_id}/media_publish', token, creation_id=parent)
    return str(result['id'])


def facebook_publish(page_id, token, images, caption):
    photo_ids = []
    for url in images:
        result = meta('POST', f'{page_id}/photos', token, url=url, published='false')
        photo_ids.append(result['id'])
    attached = {f'attached_media[{i}]': json.dumps({'media_fbid': pid})
                for i,pid in enumerate(photo_ids)}
    result = meta('POST', f'{page_id}/feed', token, message=caption, **attached)
    return str(result['id'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='YYYY-MM-DD, defaults to current date in Europe/Paris')
    args = parser.parse_args()
    day = args.date or datetime.now(ZoneInfo('Europe/Paris')).date().isoformat()
    enabled = os.getenv('PUBLISH_ENABLED', '').strip().lower() == 'true'
    if not enabled:
        print('⏸️ Publication désactivée : définir la variable GitHub PUBLISH_ENABLED à true après les tests.')
        return 0
    config = json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
    post_path = ROOT/'docs'/'posts'/day/'post.json'
    if not post_path.exists():
        print(f'❌ Aucun carrousel préparé pour {day}. Lance d’abord Générer.')
        return 1
    post = json.loads(post_path.read_text(encoding='utf-8'))
    url_root = base_url(config)
    urls = [f'{url_root}/posts/{quote(day)}/{quote(filename)}' for filename in post['images']]
    print(f'Publication {day}: vérification de {len(urls)} images hébergées sur GitHub Pages…')
    verify_public_images(urls)
    token = os.getenv('FB_PAGE_ACCESS_TOKEN', '')
    ig_id = os.getenv('IG_USER_ID', '')
    page_id = os.getenv('FB_PAGE_ID', '')
    if not token or not ig_id or not page_id:
        print('❌ Secrets manquants : FB_PAGE_ACCESS_TOKEN, IG_USER_ID ou FB_PAGE_ID.')
        return 1
    state = json.loads(STATE_FILE.read_text(encoding='utf-8')) if STATE_FILE.exists() else {}
    post_state = state.setdefault(day, {})
    failures = []
    if post_state.get('instagram'):
        print(f'Instagram déjà publié : {post_state["instagram"]}')
    else:
        try:
            result = instagram_publish(ig_id, token, urls, post['caption'])
            post_state['instagram'] = result
            state_save(state)
            print('✅ Instagram publié :', result)
        except Exception as err:
            failures.append('Instagram')
            print(f'❌ Instagram : {err}', file=sys.stderr)
    if post_state.get('facebook'):
        print(f'Facebook déjà publié : {post_state["facebook"]}')
    else:
        try:
            result = facebook_publish(page_id, token, urls, post['caption'])
            post_state['facebook'] = result
            state_save(state)
            print('✅ Facebook publié :', result)
        except Exception as err:
            failures.append('Facebook')
            print(f'❌ Facebook : {err}', file=sys.stderr)
    if failures:
        print('Échec sur : '+', '.join(failures)+'. Consulter les logs avant de relancer.')
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
