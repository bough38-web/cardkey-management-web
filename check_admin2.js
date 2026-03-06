const puppeteer = require('puppeteer');

process.on('unhandledRejection', error => {
    console.log('Node unhandledRejection:', error);
});

(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();

        page.on('console', msg => {
            console.log('BROWSER CONSOLE:', msg.type(), msg.text());
        });

        page.on('pageerror', error => {
            console.log('BROWSER ERROR:', error.message);
        });

        await page.goto('http://localhost:3000/Admin.html', { waitUntil: 'networkidle2' });

        // Wait for a little bit to ensure all scripts run
        await new Promise(resolve => setTimeout(resolve, 2000));

        await browser.close();
    } catch (e) {
        console.log("PUPPETEER EXCEPTION:", e);
    }
})();
