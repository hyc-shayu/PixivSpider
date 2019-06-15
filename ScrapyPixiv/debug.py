from scrapy import cmdline

# don't use ImagePipeline
cmdline.execute(['scrapy', 'crawl', 'pixiv1'])
# use ImagePipeline
# cmdline.execute(['scrapy', 'crawl', 'pixiv2'])
