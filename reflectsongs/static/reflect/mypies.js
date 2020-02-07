jQuery(window).on('load', function() {
    jQuery('canvas.chart').each(function() {
        var jthis = jQuery(this);
        var percs = JSON.parse(jthis.data('values'));
        var data = {
            datasets: [{
                data: [10, 20, 30]
            }],
            labels: [
                'Red',
                'Yellow',
                'Blue'
            ]
        };
        var ctx = this.getContext('2d');
        var myPieChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {}
        });
    });
});
