BASE_URL = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
LOGIN_URL = 'https://accounts.pixiv.net/api/login?lang=zh'
FIRST_PAGE = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust'
HEADERS = {
            # 'Host': "accounts.pixiv.net",
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            'Referer': "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
}
RETURN_TO = 'https://www.pixiv.net/'
PIXIV_ID = 'NDE1Mzg2MzZlYzM1@foxmail.com'
PASSWORD = '41538636ec35'
SAVE_PATH = 'E:/image'
BAD_REQUEST_RETRIES = 3
