# Pose and costume references

从以下图库下载的参考图片（保留原始 PNG）：

- https://ai-pose-gallery.pages.dev/
- https://ai-costume-gallery.pages.dev/

## 当前收录范围

- `images/pose/`：图库全部姿势类别，1,439 张。
- `images/costume/`：图库全部服装类别，1,407 张。

本次下载未筛选类别，共收录 2,846 张原始 PNG 图片；收录范围以 `manifest.json` 为准。

`manifest.json` 记录每张图片的来源、原站元数据、文件大小和 SHA-256；下载失败时会记录错误。

来源页面注明禁止批量下载及再分发。本仓库不授予这些图片的使用或再分发许可，图片权利及使用条件以原作者规定为准。

## 下载与校验

```sh
python3 scripts/download_galleries.py
# 如需使用本机代理：
GALLERY_PROXY=http://127.0.0.1:7897 python3 scripts/download_galleries.py
```

脚本可重复运行，已下载文件会验证 PNG 签名后复用，并重新生成清单。
