$('document').ready(function () {
    let getCanvas;

    html2canvas(document.querySelector(".sq")).then(canvas => {
        document.body.appendChild(canvas);
        getCanvas = canvas;
    });

    $('#download').on('click', () => {
        var imageData = getCanvas.toDataURL("image/png");
        // Now browser starts downloading it instead of just showing it
        var newData = imageData.replace(/^data:image\/png/, "data:application/octet-stream");
        $("#download").attr("download", "image.png").attr("href", newData);
    });
});