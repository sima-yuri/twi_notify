import requests
import os

import setting

import sys
sys.dont_write_bytecode = True

# LINE APIトークン
# 本番環境動作時は TOKUN_PROD に変更
LINE_TOKEN = setting.LINE_NOTIFY_TOKUN_DEV

# フィードドメイン
FEED_BASE_URL = setting.FEED_BASE_URL

# LINE APIエンドポイント
LINE_NOTIFY_API = "https://notify-api.line.me/api/notify"

twi_feed_path = 'tools/twitter_notify/src/feed/twi_feed.txt'
image_dir_path = 'tools/twitter_notify/src/image.'


# 取得したいユーザーリスト
twi_users = ['ariariarisa1121']


def get_feed_json(username, type):
    """
    FeedからItemsを取得する

    Parameters
    ----------
    username : string
        取得するユーザーネーム
    type : string
        Feedタイプ(将来的に他フィード統合予定）

    Returns
    -------
    item : 
        対象のItemフィード

    """
    # TODO: フィードURLが暫定対応（git/rss-bridgeの部分）
    if type == 'twitter':
        feed_url = '%s/git/rss-bridge/?action=display&bridge=Twitter&context=By+username&u=%s&norep=on&noretweet=on&nopic=on&noimgscaling=on&format=Json' % (
            FEED_BASE_URL, username)

    response = requests.get(feed_url)
    jsonData = response.json()
    items = jsonData.get('items')
    return items

def save_feed(items, username, type='other'):
    """
    ItemsからFeedを保存する

    Parameters
    ----------
    items : 
        投稿フィード

    """
    for item in items:
        itemUrl = item.get('id')
        images = item.get('attachments')
        title = item.get('title')

        if images is not None:
            with open(twi_feed_path, mode='r', newline='', encoding='utf-8') as f_in:
                # フィード重複フラグ
                flag = False
                lines = [line for line in f_in]
                for i in lines:
                    if itemUrl in i:
                        flag = True

                if not flag:
                    file = open(twi_feed_path, 'a', encoding='utf-8')
                    file.write(itemUrl + '\n')
                    file.close()

                    # 画像保存処理
                    save_image(images, title, itemUrl)
        else:
            print('画像なし')

def save_image(images, title=None, itemUrl=None):
    """
    画像URLから画像を保存する

    Parameters
    ----------
    images : 
        投稿フィード
    title : string
        投稿タイトル
    itemUrl : string
        投稿URL

    """
    imageIndex = 1
    imageLen = len(images)

    for image in images:
        picture = image['url']
        re = requests.get(picture)

        # 拡張子をContent-typeから取得
        fileTypes = re.headers['Content-Type'].split('/')[-1]
        fileType = "".join(fileTypes)
        # Content-typeの拡張子を画像パスにつける
        filePath = image_dir_path + fileType

        # ローカルに保存
        with open(filePath, 'wb') as f:
            f.write(re.content)

        # LINE通知
        send_line_notify(
            imageLen,
            imageIndex,
            fileType,
            title,
            itemUrl)
        imageIndex = imageIndex + 1
        
        # 削除処理
        os.remove(image_dir_path + fileType)

def send_line_notify(imageLen, index, fileType, text=None, url=None):

    headers = {'Authorization': 'Bearer ' + LINE_TOKEN}

    # 画像の枚数目でテキストメッセージ変更
    if index == 1:
        sendMassage = ' 📸テスト投稿枚数%d枚 \n\n %s \n %s' % (imageLen, text, url)
    else:
        sendMassage = ' %d枚目 / %d枚中' % (index, imageLen)

    if fileType == "jpeg":
        image_dir_path2 = image_dir_path + 'jpeg'
        payload = {'message': sendMassage}
        files = {"imageFile": open(image_dir_path2, "rb")}
        requests.post(
            LINE_NOTIFY_API,
            data=payload,
            headers=headers,
            files=files)

def main():
    try:
        # ユーザーのTwitterフィードチェック
        for twi_user in twi_users:
            items = get_feed_json(twi_user, 'twitter')
            save_feed(items, twi_user)

    except BaseException:
        print('エラー')

if __name__ == '__main__':
    main()
