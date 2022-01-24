function renderPDF(url, canvasContainer, options) {
    const pdfjs = window['pdfjs-dist/build/pdf'];
    options = options || {scale: 1.55}

    function renderPage(page, num) {
        const viewport = page.getViewport(options.scale);
        const pageContainer = document.createElement('div');
        pageContainer.setAttribute("style", "display: inline-block");
        const canvas = document.createElement('canvas');
        pageContainer.setAttribute("id", `page-${num}`);
        pageContainer.setAttribute("class", `pageContainer`);
        const context = canvas.getContext('2d');
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        canvas.height = viewport.height;
        canvas.width = viewport.width;
        pageContainer.appendChild(canvas);
        canvasContainer.appendChild(pageContainer);
        canvasContainer.scrollTop = canvasContainer.scrollHeight;

        page.render(renderContext);
    }

    function pageNumber(pdfDoc) {
        for (let page = 1; page <= pdfDoc.numPages; page++)
            pdfDoc.getPage(page).then(pageData => renderPage(pageData, page));
        // document.getElementById('pageOf').innerHTML += pdfDoc.numPages
    }

    // url = convertDataBase64ToBinary(url)
    const setPDF = pdfjs.getDocument(url + '?timestamp=' + new Date().getTime());
    setPDF.then(pageNumber)
}