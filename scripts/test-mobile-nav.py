"""Verify mobile nav: burger left of logo, Login / Sign Up visible."""
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
              const gate = document.getElementById('pgate');
              const main = document.getElementById('pmain');
              if (gate) gate.classList.remove('active');
              if (main) main.classList.add('active');
            }"""
        )

        await page.wait_for_selector("nav .navburger", state="visible", timeout=15000)

        result = await page.evaluate(
            """() => {
              const nav = document.querySelector('nav');
              const burger = nav.querySelector(':scope > .navburger');
              const logo = nav.querySelector(':scope > .wm');
              const auth = document.getElementById('navauth');
              const short = auth?.querySelector('.nlog-short');
              const br = burger.getBoundingClientRect();
              const lr = logo.getBoundingClientRect();
              const cs = getComputedStyle(short);
              return {
                burgerDirectChild: !!burger,
                burgerInNr: !!nav.querySelector('.nr .navburger'),
                burgerLeft: br.left,
                logoLeft: lr.left,
                burgerBeforeLogo: br.left < lr.left,
                shortText: short?.textContent?.trim() || '',
                shortVisible: cs.display !== 'none' && cs.visibility !== 'hidden',
                fullHidden: getComputedStyle(auth.querySelector('.nlog-full')).display === 'none',
              };
            }"""
        )

        await browser.close()

        print(result)
        fails = []
        if not result["burgerDirectChild"]:
            fails.append("hamburger is not a direct child of nav (should be left of logo)")
        if result["burgerInNr"]:
            fails.append("hamburger still inside .nr")
        if not result["burgerBeforeLogo"]:
            fails.append("hamburger is not left of logo")
        if result["shortText"] != "Login / Sign Up":
            fails.append(f'mobile auth label is "{result["shortText"]}" not "Login / Sign Up"')
        if not result["shortVisible"]:
            fails.append("nlog-short not visible on mobile")
        if not result["fullHidden"]:
            fails.append("nlog-full should be hidden on mobile")

        if fails:
            for f in fails:
                print("FAIL:", f)
            return 1
        print("PASS: mobile nav layout correct")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
