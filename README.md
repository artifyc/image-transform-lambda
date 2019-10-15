## Installation and Usage

```
$ zappa deploy production
...
Your Zappa deployment is live!: https://<address>.execute-api.us-east-1.amazonaws.com/production

$ curl -X POST https://<address>.execute-api.us-east-1.amazonaws.com/production \
  -F file=@image.png
...

{
  "yaddayadda": "https://s3.amazonaws.com/yaddayadda/image.png",
  "yaddayadda-300px": "https://s3.amazonaws.com/yaddayadda-300px/image.png",
  "yaddayadda-600px": "https://s3.amazonaws.com/yaddayadda-600px/image.png"
}
```