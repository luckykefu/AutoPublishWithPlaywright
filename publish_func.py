import asyncio
import json
import os
import random
import re
import subprocess
import frontmatter
from playwright.async_api import Playwright, async_playwright, expect
from dotenv import load_dotenv
load_dotenv()

async def init_browser(playwright): 
    print('init browser')
    browser = await playwright.chromium.launch_persistent_context(# 打开浏览器
    user_data_dir=None,# 浏览器数据保存路径
    executable_path=os.getenv('CHROME_BIN'),# 指定浏览器路径
    accept_downloads=True,# 接受下载
    headless=False,# 无头模式
    bypass_csp=True,# 绕过CSP
    slow_mo=10,# 慢速模式
    args=['--disable-blink-features=AutomationControlled'] #跳过检测
    )
    browser.set_default_timeout(60*1000)
    return browser

def get_title(filepath):
    print('get title')
    filename = os.path.splitext(os.path.basename(filepath))[0]
    return filename 

def get_content(filepath):
    print('get content')
    with open(filepath, 'r',encoding='utf-8') as f:
        content = f.read()
    return content

def get_cover(folder_path):
    print('get cover')
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # 筛选出图片文件，这里以.jpg和.png为例
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    # 随机选择一张图片
    random_image = random.choice(images) if images else None
    # 返回图片的完整路径
    return os.path.join(folder_path, random_image) if random_image else None

def md_to_doc(input_file):
    print('md to doc')
    input_file = os.path.abspath(input_file)

    file_name = os.path.splitext(input_file)[0]
    # print(f"文件名: {file_name}")
    
    output_file = f"{file_name}.docx"
    
    # 设置你的 Docx 模板路径
    template_docx = 'pandoc_word_template-main/templates_标题不编号.docx'  # 替换成你的 Docx 模板文件路径
    # print(f"模板文件: {template_docx}")

    command = [
        'pandoc', input_file,
        '--reference-doc', template_docx,
        '-o', output_file
    ]

    # 使用 subprocess.run 来执行命令
    try:
        if not os.path.exists(output_file):
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"文件成功生成在: {output_file}")

    except subprocess.CalledProcessError as error:
        print("命令执行失败")
        print(f"标准输出: {error.stdout}")
        print(f"标准错误: {error.stderr}")

    # 返回输出的文件地址
    return output_file

async def load_cookies(cookie_file, browser):
    print('load cookies')
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
        await browser.add_cookies(cookies)
    

async def save_cookies(cookie_file, page):
    print('save cookies')
    cookies = await page.context.cookies()
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f)
        
async def jianshu(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_JIANSHU')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()
    
    await page.goto('https://www.jianshu.com')
    await page.wait_for_load_state('load')
    
    is_login = await page.is_visible("#sign_in")
    if is_login:
        print('not login, try to login')
        try:
            await page.locator("#sign_in").click()
            
            async with page.expect_popup() as p1_info:
                await page.locator("a.weixin").click()
            page1 = await p1_info.value
            
            await page1.wait_for_selector('div.user')
        
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    # 写文章
    async with page.expect_popup() as p1_info:
        await page.locator("a.btn.write-btn").click()
    page2 = await p1_info.value
    # await page2.wait_for_load_state('load')
    print('写文章页面打开成功')    
    
    # 新建文章
    await page2.locator("div._1GsW5").click()
    await page2.wait_for_timeout(1000)
    print('新建文章')
    
    # 选择封面
    await page2.locator('div._3br9T li > div').click()
    await page2.locator("li").filter(has_text=re.compile(r"^设置发布样式$")).click()
    await page2.locator("input[type=\"file\"]").set_input_files(cover)
    await page2.wait_for_timeout(10000)
    await page2.get_by_role("button", name="保存").click()
    print('选择封面成功')
    
    # 填写标题
    name= get_title(file_path)
    await page2.wait_for_selector('div > input[type="text"]')
    await page2.locator('div > input[type="text"]').clear()
    await page2.locator('div > input[type="text"]').fill(name)
    await page2.wait_for_timeout(1000)
    print('填写标题成功')

    # 填写内容
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content= frontmatter.load(f)
    md_content = md_content.content
    await page2.locator("div.kalamu-area").fill('JIANSHU'+md_content)
    await page2.wait_for_timeout(1000)
    print('填写内容成功')

    # 发布文章
    await page2.wait_for_timeout(3000)
    await page2.get_by_text("发布文章").click()
    await page2.locator('a[data-action="publicize"]').click()
    await page2.wait_for_selector('a:has-text("发布成功")')
    print('publish success')
    await browser.close()
    
async def csdn(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_CSDN')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)
        
    page=await browser.new_page()
    
    url='https://www.csdn.net'
    await page.goto(url)
    await page.wait_for_load_state('load')

    logined_element = 'a.hasAvatar'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.get_by_text("登录", exact=True).click()
            await page.wait_for_selector(logined_element)
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    # 写文章
    await page.get_by_role('link', name='发布', exact=True).click()
    await page.wait_for_load_state('load')
    
    # upload md file
    async with page.expect_popup() as p1_info:
        await page.get_by_label("使用 MD 编辑器").click()
    page1 = await p1_info.value
    await page1.wait_for_load_state('load')
    await page1.locator("#import-markdown-file-input").set_input_files(file_path)
    print('upload md file success')
    
    # add tags
    await page1.get_by_role('button', name='发布文章').click()
    await page1.get_by_role('button', name='添加文章标签').hover()
    await page1.wait_for_timeout(1000)
    await page1.locator(".el-tag.el-tag--light").first.click()
    await page1.locator('.mark_selection_box_body button').click()
    print('add tags success')
    
    # set cover
    await page1.locator('div.cover-upload-box input').first.set_input_files(cover)
    await page1.wait_for_timeout(10000)
    print('set cover success')
    
    await page1.locator('.modal__button-bar button').last.click()
    await page1.wait_for_selector('a.success-modal-btn')
    print('publish success')
    await browser.close()
    
async def bilibili(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    cookies=os.getenv('COOKIES_BILIBILI')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()
    
    url='https://www.bilibili.com/'
    await page.goto(url)
    await page.wait_for_load_state('load')

    logined_element = '.v-popover-wrap.header-avatar-wrap'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.get_by_text("登录", exact=True).click()
            await page.locator("div").filter(has_text=re.compile(r"^微信登录$")).click()
            await page.wait_for_selector(logined_element)
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    # t投稿
    async with page.expect_popup() as p1_info:
        await page.get_by_role("link", name="投稿", exact=True).click()
    page1 = await p1_info.value
    await page1.wait_for_load_state('load')
    print('投稿页面打开成功')
    
    await page1.locator("#video-up-app").get_by_text("专栏投稿").click()
    print('选择专栏投稿')
    
    # title
    name = get_title(file_path)
    await page1.frame_locator("div.iframe-comp-container iframe").locator("textarea").fill(name)
    print('填写标题成功')
    
    # content
    cont = get_content(file_path)
    await page1.frame_locator("div.iframe-comp-container iframe").locator("div.ql-editor.ql-blank").fill(cont)
    print('填写内容成功')
    
    # origin
    await page1.frame_locator("div.iframe-comp-container iframe").get_by_text("更多设置").click()
    await page1.frame_locator("div.iframe-comp-container iframe").get_by_role("checkbox", name="我声明此文章为原创").click()
    await page1.frame_locator("div.iframe-comp-container iframe").locator(".bre-modal__close").click()
    print('选择原创声明')
    
    # cover
    page1.once("filechooser", lambda file_chooser: file_chooser.set_files(cover))
    await page1.frame_locator("div.iframe-comp-container iframe").locator(".bre-settings__coverbox__img").click()
    await page1.wait_for_timeout(10000)
    await page1.frame_locator("div.iframe-comp-container iframe").locator(".bre-img-corpper-modal__footer button").first.click()
    print('选择封面成功')
    
    # submit
    await page1.frame_locator("div.iframe-comp-container iframe").get_by_role("button", name="提交文章").click()
    await page1.frame_locator("div.iframe-comp-container iframe").locator(".success-image").wait_for()
    print('publish success')
    await browser.close()
       
async def baijiahao(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_BAIJIAHAO')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)
        
    page=await browser.new_page()

    url='https://baijiahao.baidu.com/'
    await page.goto(url)
    await page.wait_for_load_state('load')

    logined_element = '.author'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.locator("div.btnlogin--bI826").click()
            await page.wait_for_selector(logined_element)
        
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    # go to publish page
    await page.locator("div.nav-switch-btn").first.click()
    await page.get_by_role("button",  name= "发布" ).hover()
    await page.locator("li.edit-news").click()
    await page.wait_for_load_state("load")
    print('发布页面打开成功')
    
    # upload file
    await page.locator("#edui43_body div").first.click()
    doc=md_to_doc(file_path)
    await page.locator("span input[type='file']").set_input_files(doc)
    print('上传文件成功')
    
    # upload cover
    await page.locator("#edui33_body div").first.click()
    await page.locator("span.uploader input").set_input_files(cover)
    await page.wait_for_timeout(10 * 1000)
    await page.get_by_role("button",  name= "确 认" ).click()
    print('上传封面成功')
    
    # publish cover and setting
    await page.locator("div.edit-cover-container  input").last.click()
    await page.locator(".coverUploaderView > .container").first.click()
    await page.locator("div.cheetah-ui-pro-image-modal-choose-cover > div").click()
    await page.get_by_role("button",  name= "确 认" ).click()
    print('设置封面成功')
    
    # 发布
    await page.wait_for_timeout(10000)
    await page.locator("div.setting-item input").first.check()
    await page.wait_for_timeout(10000)
    await page.locator("div.op-btn-outter-content button").nth(1).click()
    await page.wait_for_selector('a.btn.write-another')
    await browser.close()
    print('publish success')
    os.remove(doc)
    

async def juejin(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_JUEJIN')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()
    
    url='https://www.juejin.cn'
    await page.goto(url)
    await page.wait_for_load_state('load')

    logined_element = 'div.avatar-wrapper'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.locator("button.login-button").click()
            await page.locator("div.oauth-bg").nth(1).click()
            await page.wait_for_selector(logined_element)
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    await page.get_by_role('button', name='创作者中心').click()
    await page.wait_for_load_state('load')
    print('创作者中心打开成功')

    async with page.expect_popup() as p1_info:
        await page.get_by_role('button', name='写文章').click()
    page1 = await p1_info.value
    await page1.wait_for_load_state('load')
    await page1.locator('div.bytemd-toolbar-icon.bytemd-tippy.bytemd-tippy-right[bytemd-tippy-path="6"]').click()
    print('选择编辑器')

    await page1.locator('div.upload-area > input[type="file"]').set_input_files(file_path)
    print('上传文件成功')

    name = get_title(file_path)
    await page1.locator("input.title-input").fill(name)
    print('填写标题成功')
    
    # 发布设置
    await page1.get_by_role("button",  name= "发布" ).click()
    await page1.locator("div.item").nth(4).click()
    await page1.locator("div.byte-select__wrap").first.click()
    await page1.get_by_role("button",  name= "GitHub" ).click()
    await page1.locator("div.summary-textarea > textarea").fill("A"*100)
    
    # cover
    page1.once("filechooser", lambda file_chooser: file_chooser.set_files(cover))
    await page1.locator("div.button-slot").click()
    await page1.wait_for_timeout(10000)
    
    await page1.get_by_role("button",  name= "确定并发布" ).click()
    await page1.wait_for_selector('div.thanks')
    await browser.close()  
    print('publish success')      
       
async def tencentcloud(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_TENCENTCLOUD')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()

    url='https://cloud.tencent.com/developer'
    await page.goto(url)
    await page.wait_for_load_state('load')

    istips= await page.is_visible("button.cdc-btn.mod-activity__btn.cdc-btn--hole")
    if istips:
        await page.get_by_role("button",  name= "不再提示" ).click()
        
    logined_element = 'i.cdc-header__account-avatar'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.get_by_role('button', name='登录/注册').click()
            await page.wait_for_selector(logined_element)
            print('wait for user img locator:', logined_element)
        
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
    print('login success')
    await save_cookies(cookies, page)
    
    await page.get_by_text('发布').click()
    await page.get_by_role('link', name= '写文章' ).click()
    await page.wait_for_load_state('load')
    print('写文章页面打开成功')
    
    
    name = get_title(file_path)
    await page.locator('div.article-title-wrap  textarea').fill(name)
    print('填写标题成功')

    doc= md_to_doc(file_path)
    await page.locator('.qa-r-editor-btn.select-file input[accept=".docx"]').set_input_files(doc)
    print('上传文件成功')
    
    await page.get_by_role('button', name= '发布' ).click()
    await page.get_by_label('原创').click()
    await page.locator('.com-2-tag-input').first.fill("github")
    await page.locator('.com-2-tagsinput-dropdown-menu li').first.click()
    await page.wait_for_timeout(2000)
    
    # cover
    await page.locator('#editor-upload-input').set_input_files(cover)
    print('上传封面成功')
    
    await page.get_by_role('button', name= '确认发布' ).click()
    await page.wait_for_selector('.col-editor-feedback-icon')
    await browser.close()
    os.remove(doc)
    print('publish success')     


async def toutiao(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_TOUTIAO')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()
    
    url='https://www.toutiao.com/'
    await page.goto(url)
    await page.wait_for_load_state('load')
    try:
        await page.locator("button.add-btn").wait_for()
        await page.locator("button.add-btn").hover()
    except:
        pass
    
    logined_element = 'div.user-icon span'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.locator("div.toutiao-header a.login-button").wait_for()
            await page.locator("div.toutiao-header a.login-button").click()
            await page.get_by_label("协议勾选框").click()
            async with page.expect_popup() as popup_info:
                await page.get_by_role("button", name="微信登录").click()
            page1= await popup_info.value
            await page1.wait_for_selector(logined_element)
            print('wait for user img locator:', logined_element)
        
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
    else:
        page1=page
    
    print('login success')
    await save_cookies(cookies, page)
    
    async with page1.expect_popup() as popup_info:
        await page1.locator("a.publish-item").first.click()
    page2 = await popup_info.value
    await page2.wait_for_load_state('load')
    await (await page2.wait_for_selector("span.icon-wrap")).click()
    print('写文章')

    doc = md_to_doc(file_path)
    await page2.locator('div.doc-import button').click()
    await page2.locator(' div.upload-handler input').set_input_files(doc)
    print('上传文件成功')

    await page2.wait_for_timeout(5000)
    name = get_title(file_path)
    await page2.locator("div.editor-title textarea").fill(name)
    await page2.wait_for_timeout(1000)
    print('填写标题成功')


    await page2.locator("label").filter(has_text="单标题").locator("div").click()
    
    # cover
    await page2.locator(".article-cover-add").click()
    await page2.locator('button input').set_input_files(cover)
    await page2.wait_for_timeout(10000)
    await page2.locator('div.resource-select div').click()
    await page2.get_by_role("button", name="确定").click()
    print('上传封面成功')
    
    await page2.locator("span").filter(has_text="声明原创").nth(1).click()
    # await page2.locator("#originalBtn div").first.click()
    print('选择原创声明')
    
    await page2.get_by_role("button", name="预览并发布").click()
    
    try:
        print('等待仍要发布警告')
        await page2.locator("button").filter(has_text="仍要发布").wait_for()
        await page2.locator("button").filter(has_text="仍要发布").click()
    except:
        pass
    

    await page2.get_by_role("button", name="确认发布").wait_for()
    await page2.get_by_role("button", name="确认发布").click()
    await page2.locator("button").filter(has_text="获取验证码").wait_for()
    await page2.locator("button").filter(has_text="获取验证码").click()
    print('获取验证码成功')
    
    await page2.wait_for_selector('div.byte-modal-footer', state='hidden')
    await page2.locator('div.publish-footer  button').last.click()
    await page2.wait_for_timeout(1000)
    await page2.locator('div.publish-footer  button').last.click()
    print('publish success')
    os.remove(doc)    

 
async def zhihu(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_ZHIHU')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()
    
    url='https://www.zhihu.com'
    await page.goto(url)
    await page.wait_for_load_state('load')

    logined_element = "button.GlobalWriteV2-topItem"
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.locator(".Login-socialButtonGroup > button").first.click()
            await page.wait_for_selector(logined_element)
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    async with page.expect_popup() as popup_info:
        await page.get_by_role("button",name='写文章').click()
    page2 = await popup_info.value
    await page2.wait_for_load_state('load')
    print('写文章页面打开成功')
    
    name=get_title(file_path)
    await page2.locator('textarea').fill(name)
    print('填写标题成功')
    
    await page2.get_by_label("文档").click()
    await page2.locator("#Popover5-content").get_by_label("文档").click()
    await page2.locator('form input').set_input_files(file_path)
    print('上传文件成功')
    

    await page2.locator("label input[type='file']").set_input_files(cover)
    print('上传封面成功')
    
    # add 话题
    await page2.get_by_role("button", name="添加话题").click()
    await page2.locator("input[aria-label='搜索话题']").fill("github")
    await page2.locator('div.Popover-content button').first.click()
    print('添加话题成功')
    
    await page2.wait_for_timeout(10000)
    await page2.get_by_role("button", name="发布", exact=True).click()
    await page2.get_by_role("button", name="写文章", exact=True).wait_for()
    await browser.close()
    print('publish success')
 
async def wxgzh(p):
    file_path = os.getenv('FILE_PATH')
    cover=get_cover(os.getenv('COVER_PATH'))
    browser=await init_browser(p)
    
    cookies=os.getenv('COOKIES_WXGZH')
    if os.path.exists(cookies):
        await load_cookies(cookies, browser)

    page=await browser.new_page()
    
    url='https://mp.weixin.qq.com/'
    await page.goto(url)
    await page.wait_for_load_state('load')

    logined_element = '.weui-desktop-account__img'
    is_login = await page.is_visible(logined_element)
    if not is_login:
        print('not login, try to login')
        try:
            await page.wait_for_selector(logined_element)
            print('wait for user img locator:', logined_element)
        
        except Exception as e:
            print('login failed, try again \n error:', e)
            await page.close()
            return
        
    print('login success')
    await save_cookies(cookies, page)
    
    async with page.expect_popup() as p1_info:
        await page.locator(".new-creation__menu-content").first.click()
    page1 = await p1_info.value
    await page1.wait_for_load_state('load')
    print('打开新建文章页面成功')
    
    await page1.get_by_role("listitem", name="文档导入").click()
    doc = md_to_doc(file_path)
    await page1.locator(".weui-desktop-upload input").set_input_files(doc)
    print('上传文件成功')
    
    author="kefu1252"
    await page1.get_by_placeholder("请输入作者").fill(author)
    print('fill author:', author)
    
    # upload cover image
    await page1.wait_for_selector(".select-cover__btn")
    await page1.locator(".select-cover__btn").hover()
    await page1.get_by_role("link", name="从图片库选择").click()
    await page1.locator('input[multiple="multiple"]').set_input_files(cover)
    await page1.wait_for_timeout(10*1000)
    await page1.locator('div.selected.weui-desktop-img-picker__item').wait_for()
    await page1.get_by_role("button", name="下一步").click()
    await page1.wait_for_timeout(10000)
    await page1.get_by_role("button", name="完成").wait_for()
    await page1.get_by_role("button", name="完成").click()
    print("封面")
    
    # 原创声明
    await page1.locator("#js_original").click()
    await page1.locator("i.weui-desktop-icon-checkbox").click()
    await page1.get_by_role("button", name="确定").click()
    print("原创声明")

    await page1.locator("#js_reward_setting_area").click()
    await page1.wait_for_timeout(3000)
    await page1.get_by_role("button", name="确定").click()
    print("赞赏")
    
    await page1.wait_for_timeout(1000)
    await page1.get_by_role("button", name="发表").click()
    print("发表")
    
    await page1.locator("#vue_app").get_by_role("button", name="发表").wait_for()
    await page1.locator("#vue_app").get_by_role("button", name="发表").click()
    await page1.get_by_role("button", name="继续发表").click()
    print("继续发表")
    print("扫码验证")
    await page1.wait_for_selector(".weui-desktop-account__img")
    print("发布成功")
    await browser.close()
    os.remove(doc)
    print('publish success')   
    
async def main():
    
    async with async_playwright() as p:
        
        # await jianshu(p)
        # await csdn(p)
        # await bilibili(p)
        # await baijiahao(p)
        # await juejin(p)
        # await tencentcloud(p)
        await toutiao(p)
        await zhihu(p)
        # await wxgzh(p)
        
if __name__ == '__main__':

    asyncio.run(main())
