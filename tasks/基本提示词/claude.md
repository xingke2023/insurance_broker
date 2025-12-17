在 Django 管理后台添加一个灵活的页面权限管理功能。这样你就可以通过后台界面配置哪些用户组可以访问哪些页面

重启后端 Django 服务的命令：
sudo supervisorctl restart harry-insurance:harry-insurance-django
重启前端，目前前端是nginx静态目录，所以只需要到frontend目录进行构建就好 npm run build

现在修改 CompanyComparison 页面，根据用户设置过滤显示产品。首先查看 fetchCompanies 的相关代码
每个用户都可以自定义自己想要对比的保险产品了。