# Configuration variables (URLs, timeouts, etc.)
# Application URLs
LOGIN_URL = 'https://www.zhipin.com/web/user/?intent=0&ka=header-geek'
JOB_RECOMMEND_URL = 'https://www.zhipin.com/web/geek/job-recommend'
# company scale ==》》302=20-99人, 303=100-499人， 304=500-999人 &scale=302,303,304,305,306
# 100101 = java, 100102=c/c++, PHP=100103,
# need to change job position in each iteration of job position
# need to run again
JOB_QUERY = '/web/geek/job?query=&city=100010000'
COMPANY_DETAILS_URI = "/gongsi/663dbda1440012971HB43dW9GVA~.html?ka=job-cominfo"
BASE_URL = 'https://www.zhipin.com'
IT_POSITIONS = [100124, 100125, 100123, 100901, 100202, 100203, 100209, 100211, 100210, 100212, 100208, 100213, 100301, 100309, 100302, 100303, 100305, 100308, 100307, 100304, 100310, 100703, 100401, 100405, 100403, 100407, 100404, 100402, 100406, 100409, 290166,
                100408, 100410, 101306, 100117, 101310, 100104, 101311, 101312, 100118, 100115, 101305, 101309, 100120, 101307, 101301, 101302, 101308, 130121, 101201, 101202, 101299, 160303, 100511, 100508, 100507, 100506, 100512, 100514, 100122, 100515, 100601, 100606, 100605, 100607, 100817, 100603, 100701, 100704, 100702, 100705, 100707, 100706, 101101]
# File paths
COOKIE_FILE = 'userSecret/cookies.json'

# Timeouts
LOGIN_TIMEOUT = 60
PAGE_LOAD_TIMEOUT = 10
