var stylesheets = ['main'];

for (var i = 0; i < stylesheets.length; i++) {
    var id = stylesheets[i] + 'CSSID';

    if (!document.getElementById(id)) {
        //Accesses data at https://mjjbennett.github.io/resources/stylesheets/
        var css_path = 'https://gp.forricide.me/resources/stylesheets/' + stylesheets[i] + '.css';
        console.log('Injecting stylesheet: ' + css_path);
        var link = document.createElement('link');
        link.id = id;
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = css_path;
        document.getElementsByTagName('head')[0].appendChild(link);
    }
}

