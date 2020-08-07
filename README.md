# 爬虫项目



## 1、目录结构描述
```

├── README.md                   // readme
├── main.py                     // 主文件
└── tmp                         
    └── backup
        └── 20200807141729      // 每次的获取结果 按时间
            ├── css             // 存储css文件
            ├── image           // 存储图片文件
            ├── js              // 存储js文件
            └── index.html      // html文件
```


## 2、启动命令

- `python main.py -u http://m.sohu.com/limit/  -d 23 -o tmp/backup`

### 2.1 参数说明

- `-u 抓取的目标网址  以 http://或者https:// 开头`
- `-d 爬取的时间间隔 int类型`
- `-o 结果存储路径，以当前项目路径为基准`

## 3、结束命令

- `Ctrl+C`

## 4、环境说明

```
本项目基于python3.7环境
```