Offensive Web Testing Framework
===

[![Requirements Status](https://requires.io/github/owtf/owtf/requirements.svg?branch=develop)](https://requires.io/github/owtf/owtf/requirements/?branch=develop)
[![Build Status](https://travis-ci.org/owtf/owtf.svg?branch=develop)](https://travis-ci.org/owtf/owtf)
[![License (3-Clause BSD)](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg?style=flat-square)](http://opensource.org/licenses/BSD-3-Clause)
[![python](https://img.shields.io/badge/python-2.7-blue.svg)](https://www.python.org/downloads/)
[![python](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/)

<img src="https://www.owasp.org/images/7/73/OWTFLogo.png" height="150" width="120" />

**OWASP OWTF** 是一个着眼于高效渗透测试以及与OWASP测试指南标准（OWASP Testing Guide (v3 and v4)）、OWASP top 10、PTES和NIST保持一致性的安全测试的项目，这样渗透人员能有更多的时间去：

- See the big picture and think out of the box
- 更高效地发现，验证和结合分析漏洞
- 调查复杂的漏洞，比如业务逻辑/设计缺陷或者虚拟主机会话
- 在疑似危险的地方进行更多的模糊测试（fuzz）
- 在通常给定的短暂测试时限内，验证影响。

这个工具是高度可定制化的，任何人都可以在没有任何开发经验的情况下，创建简单的插件或者在配置文件中添加新的测试。

> **贴士**: 当然，这个工具不会是枚“银弹”，只有当人们
在证明（漏洞）影响的时候，正确地去阐释工具的输出，决定好进一步的探究方向，积累了足够的经验，这个工具才能发挥最好的功用。


需求：
===

OWASP实在Kali Linux和MacOS上开发的，但是它是为Kali Linux（或者其他Debian系）定制的。

OWTF同时支持Python2和Python3。

安装：
===

推荐方式：

> 首选方式：Virtualenv

`pip install owtf` 或者 `pip install git+https://github.com/owtf/owtf#egg=owtf` 或者克隆这个仓库然后运行 `python setup.py install`

在Windows或者MacOS上运行OWTF，清使用供OWTF运行的Dockerfile（需要安装了**Docker**）：

 - `make docker-build`
 - `make docker-run`
 - 打开 `~/.owtf/conf` 再将 `SERVER_ADDR: 127.0.0.1` 改为 `SERVER_ADDR: 0.0.0.0`.
 - 创建一个virtualenv：`virtualenv env` 启用它： `source env/bin/activate`.
 - 安装和运行OWTF。
 
  ```bash
   $ cd owtf/
   # 安装开发者版本，这样任何修改均会即刻展现出来。
   $ python setup.py develop
   # 运行OWTF！
   $ python -m owtf
  ```
 - 开启 `localhost:8009` ，获取OWTF的web界面。

## 在OSX上安装：

安装条件：安装homebrew (https://brew.sh/) 然后跟随一下步骤：
 
```bash
 $ virtualenv <venv name>
 $ source <venv name>/bin/activate
 $ brew install coreutils gnu-sed openssl
 #我们需要先安装'cryptography'，避免出问题。
 $ pip install cryptography --global-option=build_ext --global-option="-L/usr/local/opt/openssl/lib" --global-option="-I/usr/local/opt/openssl/include"
 $ git clone <this repo>
 $ cd owtf
 $ python setup.py install
 # 运行OWTF！
 $ python -m owtf
```

为了运行工具，安装它们，并将OWTF config（~/.owtf/conf/general.cfg）指向正确的地址。

特征：
===

- **弹性**: 如果一个工具崩溃了，**OWTF**将继续转到下一个工具/测试，并自动保存输出部分直到它彻底崩溃。

- **灵活性**: 暂停和恢复你的工作。

- **测试分离**: **OWTF** 将其目标流量主要分为3类，插件：

  - **被动** : 没有流量流向目标
  - **半被动** : 正常流量到达目标
  - **主动**:  直接的漏洞探测流量

- 可扩展REST API。

- 几乎完整囊括 OWASP Testing Guide(v3, v4), Top 10, NIST, CWE标准。

- **Web界面**: 轻松管理大型渗透测试项目

- **互动报告**:
  - 从工具的输出中**自动**评级的插件，完全支持用户自定义。
  - **自定义**风险等级。
  - 每个插件都有**在线编辑器**。


许可
===

点击 [LICENSE](LICENSE.md)

链接
===

- [项目主页](http://owtf.github.io/)
- [IRC](http://webchat.freenode.net/?randomnick=1&channels=%23owtf&prompt=1&uio=MTE9MjM20f)
- [维基百科](https://www.owasp.org/index.php/OWASP_OWTF)
- [Slack](https://owasp.herokuapp.com) and join channel `#project-owtf`
- [User Documentation](http://docs.owtf.org/en/latest/)
- [油管频道](https://www.youtube.com/user/owtfproject)
- [Slideshare](http://www.slideshare.net/abrahamaranguren/presentations)
- [博客](http://blog.7-a.org/search/label/OWTF)
