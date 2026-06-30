"""Verify mobile product page: full image + variant switching."""
import asyncio
import sys
from playwright.async_api import async_playwright


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        await page.goto(url, wait_until="domcontentloaded", timeout=120000)
        await page.evaluate(
            """() => {
              document.getElementById('pgate')?.classList.remove('active');
              document.getElementById('pmain')?.classList.add('active');
            }"""
        )
        await page.evaluate("showProd('glp3rt')")

        await page.wait_for_selector("#pdmainimg", state="visible", timeout=15000)
        await page.wait_for_selector(".pdvars .pdvar", state="visible")

        layout = await page.evaluate(
            """() => {
              const img = document.getElementById('pdmainimg');
              const cs = getComputedStyle(img);
              const hero = document.querySelector('.pdhero');
              const vars = document.querySelector('.pdvars');
              const ir = img.getBoundingClientRect();
              const vr = vars.getBoundingClientRect();
              return {
                objectFit: cs.objectFit,
                varsVisible: getComputedStyle(vars).display !== 'none',
                varsLeftOfImg: vr.right <= ir.left + 4,
                heroFlex: getComputedStyle(hero).display === 'flex',
                mobileHd: getComputedStyle(document.querySelector('.pd-mobile-hd')).display !== 'none',
                src0: img.src,
              };
            }"""
        )

        await page.click(".pdvars .pdvar:nth-child(2)")
        await page.wait_for_timeout(400)

        after = await page.evaluate(
            """() => {
              const img = document.getElementById('pdmainimg');
              const active = document.querySelector('.pdvar.active')?.textContent?.trim();
              const sz = document.getElementById('szsel')?.textContent?.trim();
              return { src1: img.src, active, sz, objectFit: getComputedStyle(img).objectFit };
            }"""
        )

        await browser.close()
        print("layout:", layout)
        print("after click:", after)

        fails = []
        if layout["objectFit"] != "contain":
            fails.append(f"image object-fit is {layout['objectFit']}, expected contain")
        if not layout["varsLeftOfImg"]:
            fails.append("variant pills not left of image")
        if not layout["mobileHd"]:
            fails.append("mobile header not visible")
        if layout["src0"] == after["src1"]:
            fails.append("image did not change when variant selected")
        if after["active"] != "10mg":
            fails.append(f"active variant is {after['active']}, expected 10mg")
        if after["sz"] != "10mg":
            fails.append(f"size label is {after['sz']}, expected 10mg")

        if fails:
            for f in fails:
                print("FAIL:", f)
            return 1
        print("PASS: mobile product page")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
