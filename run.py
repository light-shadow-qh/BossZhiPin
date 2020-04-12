import os
import sys
from spider.spider import JobSpider

sys.path.append(os.path.abspath(__file__))

if __name__ == '__main__':
    job_spider = JobSpider()
    job_spider.run()