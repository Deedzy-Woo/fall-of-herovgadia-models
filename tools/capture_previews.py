"""Validate the offline viewer and capture flat-shaded Minecraft-style previews."""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

OUT=Path(__file__).resolve().parents[1]/'dead_harpy'

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,
            args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader'])
        page=await browser.new_page(viewport={'width':1600,'height':1200})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        await page.route('http://**/*',lambda r:r.abort())
        await page.route('https://**/*',lambda r:r.abort())
        await page.set_content((OUT/'dead_harpy_viewer.html').read_text(),wait_until='load')
        await page.wait_for_function('window.HarpyViewer && HarpyViewer.model.children[0].material.map.image.complete && HarpyViewer.renderer.info.render.triangles>0')
        await page.screenshot(path=str(OUT/'previews/interactive_viewer.png'))
        report=await page.evaluate('''()=>({meshes:HarpyViewer.model.children.length,triangles:HarpyViewer.renderer.info.render.triangles,texture:[HarpyViewer.model.children[0].material.map.image.naturalWidth,HarpyViewer.model.children[0].material.map.image.naturalHeight]})''')
        for text,expr in [('Сзади','HarpyViewer.camera.position.z>0'),('Каркас','HarpyViewer.wire.visible'),('Суставы','HarpyViewer.rig.visible'),('Сброс','!HarpyViewer.rig.visible&&!HarpyViewer.wire.visible')]:
            await page.get_by_role('button',name=text,exact=True).click()
            assert await page.evaluate(expr)
        await page.add_style_tag(content='header,.status,footer,nav,#notice{display:none!important}')
        for name in ('hero','front','back','side'):
            await page.evaluate('(name)=>HarpyViewer.view(name)',name)
            await page.screenshot(path=str(OUT/f'previews/{name}.png'))
        await page.evaluate('''()=>{const v=HarpyViewer;v.camera.position.set(35,44,-110);v.controls.target.set(0,32,-2);v.camera.zoom=3.7;v.camera.updateProjectionMatrix();v.controls.update();v.draw()}''')
        await page.screenshot(path=str(OUT/'previews/face_detail.png'))
        await page.evaluate('''()=>{const v=HarpyViewer;v.camera.position.set(110,37,-34);v.controls.target.set(0,32,-5);v.camera.zoom=4.2;v.camera.updateProjectionMatrix();v.controls.update();v.draw()}''')
        await page.screenshot(path=str(OUT/'previews/beak_profile.png'))
        await page.evaluate('''()=>{const v=HarpyViewer,m=v.model.children.find(m=>m.name==='left_wing_wrist'),t=new THREE.Vector3();new THREE.Box3().setFromObject(m).getCenter(t);v.camera.position.copy(t).add(new THREE.Vector3(13,7,-28));v.controls.target.copy(t);v.camera.zoom=4.2;v.camera.updateProjectionMatrix();v.controls.update();v.draw()}''')
        await page.screenshot(path=str(OUT/'previews/wing_claw_detail.png'))
        await page.evaluate('''()=>{const v=HarpyViewer;v.camera.position.set(24,43,95);v.controls.target.set(0,31.5,1);v.camera.zoom=3.3;v.camera.updateProjectionMatrix();v.controls.update();v.draw()}''')
        await page.screenshot(path=str(OUT/'previews/hair_back_detail.png'))
        report.update(page_errors=errors,offline_html_render=True,camera_buttons=True,
                      wireframe_toggle=True,rig_toggle=True,reset=True)
        (OUT/'viewer_validation.json').write_text(json.dumps(report,indent=2))
        assert not errors
        print(json.dumps(report,indent=2))
        await browser.close()

asyncio.run(main())
