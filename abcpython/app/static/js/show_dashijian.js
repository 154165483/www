$(document).ready(function () {
    var bigEvent = [{
        'year': 2017,
        'events': [
            {
                'mouths': 6,
                'times': '2017年6月2',
                'even': '刚接触python就对其无法忘怀，决定建立一个网站将自己所学的所想的记录。'
            }, {
                'mouths': 7,
                'times': '2017年7月5日',
                'even': '看过《Flask Web开发：基于Python的Web应用开发实战》，决定用flask来制作。'
            }, {
                'mouths': 10,
                'times': '2017年10月3',
                'even': '试用在阿里云上申请使用，并初步搭建网站环境：flask+nginx+uwsgi+mysql+bootstrap。'
            }, {
                'mouths': 10,
                'times': '2017年10月19日',
                'even': '注册域名abcpython.com。寓意为初学python，作者本人也是初学者。'
            }, {
                'mouths': 12,
                'times': '2017年12月5日',
                'even': '要备案，将部署在阿里云的测试服务器搬到了DigitalOcean。'
            },{
                'mouths': 12,
                'times': '2017年12月25日',
                'even': '弄了一个腾讯云2000代金券，兑换香港机器3年，就将网站搬到了腾讯云。'
            }]
    }, {
        'year': 2018,
        'events': [
            {
                'mouths': 1,
                'times': '2018年1月1',
                'even': '初学python网经过一个多月的折腾正式上线！'
            },{
                'mouths': 1,
                'times': '2018年1月21',
                'even': '写下第一篇文章《Python基础 - CentOS+Uwsgi+Nginx部署Flask应用》'
            }
        ]
    }];
    $('.event_wrap').eventFlow({'events': bigEvent});
})

