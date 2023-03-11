
Lampa.SettingsApi.addParam({
    component: 'server',
    param: {
        name: 'torrserv',
        type: 'select',
        values: TORRSERV_HOSTING,
        default: 0
    },
    field: {
        name: 'Бесплатно',
        description: 'Нажмите для выбора сервера из списка'
    },
    onChange: function (value) {
        Lampa.Storage.set('torrserver_url_two', TORRSERV_URLS[value]);
        Lampa.Storage.set('torrserver_use_link', (value == '0') ? 'one' : 'two');
        Lampa.Settings.update();
    },
    onRender: function (item) {
        setTimeout(function() {
            if ($('div[data-name="torrserv"]').length > 1) item.hide();
            //if (Lampa.Platform.is('android')) Lampa.Storage.set('internal_torrclient', true);
            $('.settings-param__name', item).css('color', 'f3d900');
            $('div[data-name="torrserv"]').insertAfter('div[data-name="torrserver_use_link"]');
        }, 0);
    }
});
})();
