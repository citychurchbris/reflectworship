jQuery(window).on('load', function() {
    jQuery('canvas#trinity-count').each(function() {
        var tdata = JSON.parse(
            document.getElementById('trinity-count-data').textContent);
        var values_by_count = [];
        var values_by_song = [];
        var labels = [];
        var colors = [
            "#FFCD56",
            "#FF6383",
            "#36A2EB"
        ];
        for (let item of tdata) {
            values_by_count.push(item.count);
            values_by_song.push(item.songs);
            labels.push(item.name);
        }
        var jthis = jQuery(this);
        var data = {
            datasets: [{
                label: "By Count",
                data: values_by_count,
                backgroundColor: colors
            }, {
                label: "By Song",
                data: values_by_song,
                backgroundColor: colors
            }],
            labels: labels
        };
        console.log(data);
        var ctx = this.getContext('2d');
        var myPieChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: {}
        });
    });
});
