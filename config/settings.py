# Configuration variables (URLs, timeouts, etc.)
# Application URLs
LOGIN_URL = 'https://www.zhipin.com/web/user/?intent=0&ka=header-geek'
JOB_RECOMMEND_URL = 'https://www.zhipin.com/web/geek/job-recommend'
# company scale ==》》302=20-99人, 303=100-499人， 304=500-999人 &scale=302,303,304,305,306
# 100101 = java
JOB_QUERY = '/web/geek/job?query=&city=100010000&position=100101'
COMPANY_DETAILS_URI = "/gongsi/663dbda1440012971HB43dW9GVA~.html?ka=job-cominfo"
BASE_URL = 'https://www.zhipin.com'

# File paths
COOKIE_FILE = 'userSecret/cookies.json'

# Timeouts
LOGIN_TIMEOUT = 60
PAGE_LOAD_TIMEOUT = 10
