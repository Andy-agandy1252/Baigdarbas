// display data in a chart
window.onload = function() {
    var chart = new CanvasJS.Chart("chartContainer", {
        theme: "light2",
        animationEnabled: true,
        zoomEnabled: true,
        data: [{
            type: "line",
            dataPoints: []
        }]
    });
    var cryptoId = document.getElementById("chartContainer").getAttribute("data-crypto-id");
    fetch("/static/historydata/" + cryptoId + "_prices.csv")
        .then(response => response.text())
        .then(data => {
            processData(data);
            chart.render();
        });
    function processData(allText) {
        var allLines = allText.split(/\r\n|\n/);
        for (var i = 1; i < allLines.length; i++) {
            var data = allLines[i].split(',');
            var date = new Date(data[0]);
            var price = parseFloat(data[1]);
            chart.options.data[0].dataPoints.push({
                x: date,
                y: price
            });
        }
    }
}
// drop down nawbar
$(document).ready(function(){
  $('.nav-item.dropdown').hover(
    function(){
      $(this).find('.dropdown-menu').addClass('show');
    },
    function(){
      var dropdownMenu = $(this).find('.dropdown-menu');
      var dropdownLink = $(this).find('.dropdown-toggle');
      var dropdownItems = dropdownMenu.find('.dropdown-item');
      dropdownMenu.mouseenter(function(){
        dropdownMenu.addClass('show');
      });
      dropdownMenu.mouseleave(function(){
        dropdownMenu.removeClass('show');
      });
      dropdownLink.mouseenter(function(){
        dropdownMenu.addClass('show');
      });
      dropdownItems.mouseenter(function(){
        dropdownMenu.addClass('show');
      });
    }
  );
});


