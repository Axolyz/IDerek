# IDerek
成语单OCR结果格式化改错查询释义并输出。用于应对学校任务。极其业余，大神轻喷。
采用百度汉语源。
# F&Q
# 关于原理：
通过百度汉语的（伪）API接口抓取词条页面，符合字数类型且百度汉语中能查到的视为正确。
# 关于xp版：
xp版本质上就是Python2版。
目前已放弃对xp版的维护，也不会同步更新更多一颗赛艇的功能(求求您了装个win7吧。
由于未知原因，某个子线程在Python3一切正常，移植到Python2，子线程执行完毕但卡死了，毫无头绪。
举双手双脚欢迎各位大神pull一下这个request。
# 关于输字数类型：
主要是出于改错的精密性，某些OCR常常会智障地把一个成语中的部分汉字识别为符号，数字或字母，或者成语中间有空格，一经格式化后只剩下一两个字，如果只有一两个字，查错就会有可能判定其为正确。
# 那如果一个成语识别出来没有一个是汉字怎么办？
……无解。换个OCR吧少年。
# 关于彩蛋：
一**气！
