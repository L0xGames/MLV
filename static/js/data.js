// VUE.components für Darstellung von CSV-Daten mit BootstrapVue
Vue.component('app-user', {
    data: function () {
        return {
            test22: "keck",
            items: [
                {
                    heading1: 'd_var',
                    heading2: '22222',
                    heading3: 'table cell',
                    heading4: 'table cell',
                    heading5: 'table cell',
                    heading6: 'table cell',
                    heading7: 'table cell',
                    heading8: 'table cell',
                    heading9: 'table cell',
                    heading10: 'table cell',
                    heading11: 'table cell',

                },
                {
                    heading1: 'table cell',
                    heading2: 'table cell',
                    heading3: 'table cell',
                    heading4: 'table cell',
                    heading5: 'table cell',
                    heading6: 'table cell',
                    heading7: 'table cell',
                    heading8: 'table cell',
                    heading9: 'table cell',
                    heading10: 'table cell',
                    heading11: 'table cell',

                },
                {
                    heading1: 'table cell',
                    heading2: 'table cell',
                    heading3: 'table cell',
                    heading4: 'table cell',
                    heading5: 'table cell',
                    heading6: 'table cell',
                    heading7: 'table cell',
                    heading8: 'table cell',
                    heading9: 'table cell',
                    heading10: 'table cell',
                    heading11: 'table cell',

                },
                {
                    heading1: 'table cell',
                    heading2: 'table cell',
                    heading3: 'table cell',
                    heading4: 'table cell',
                    heading5: 'table cell',
                    heading6: 'table cell',
                    heading7: 'table cell',
                    heading8: 'table cell',
                    heading9: 'table cell',
                    heading10: 'table cell',
                    heading11: 'table cell',

                },
                {
                    heading1: 'table cell',
                    heading2: 'table cell',
                    heading3: 'table cell',
                    heading4: 'table cell',
                    heading5: 'table cell',
                    heading6: 'table cell',
                    heading7: 'table cell',
                    heading8: 'table cell',
                    heading9: 'table cell',
                    heading10: 'table cell',
                    heading11: 'table cell',

                }
            ]
        };

    },
    // table for displaying data from csv
    template: '<div>' +
        '<b-table responsive="true" head-variant="dark" no-border-collapse="true" bordered="true"  :items="items"></b-table>' +
        '</div>'
    , methods: {
        sorting(dict) {
            unsorted = []
            for (d in dict) {
                unsorted.push(d)
            }
            unsorted.sort()
            console.log(unsorted)
            sorted_dict = {};
            for (i = 0; i < unsorted.length; i++) {
                sorted_dict[unsorted[i]] = dict[unsorted[i]];
                return sorted_dict
            }
        },
        getcsvext() {
            {
                //get infos from flask api

            }
            var self = this;
            axios
                .get('http://127.0.0.1:5000/api/csvtable') // API request for csv data
                .then(function (response) {
                    self.items = response.data
                }).catch(error => console.log(error));
        }
    }, mounted() {
        this.getcsvext();
    }
});
Vue.component('infocard', {
    data: function () {
        return {
            data: {
                CSVSIZE: null,
                COLUMN: null,
                NAME: null,
                ROWS: null
            }
        }
    },
    delimiters: ['${', '}'],
    // card for displaying metadata
    template: '<div>' +
        '<div class="card-deck">' +
        ' <b-card ' +
        ' border-variant="dark"' +
        'header="Size"' +
        'header-bg-variant="dark"' +
        ' header-text-variant="white"' +
        ' align="center">' +
        ' <b-card-text >${ data.CSVSIZE }B </b-card-text>' +
        '</b-card>' +
        ' <b-card ' +
        ' border-variant="dark"' +
        'header="Column"' +
        'header-bg-variant="dark"' +
        ' header-text-variant="white"' +
        ' align="center">' +

        ' <b-card-text> ${ data.COLUMN } </b-card-text>' +
        '</b-card>' +
        ' <b-card ' +
        ' border-variant="dark"' +
        'header="Name"' +
        'header-bg-variant="dark"' +
        ' header-text-variant="white"' +
        ' align="center">' +

        ' <b-card-text>${ data.NAME }</b-card-text>' +
        '</b-card>' +
        ' <b-card ' +
        ' border-variant="dark"' +
        'header="Rows"' +
        'header-bg-variant="dark"' +
        ' header-text-variant="white"' +
        ' align="center">' +

        ' <b-card-text>${ data.ROWS }</b-card-text>' +
        '</b-card>' +
        '</div >' +
        '</div>'
    , methods: {
        getInfos() {
            {
                //get infos from flask api

            }
            var self = this;
            axios
                .get('http://127.0.0.1:5000/api/csvinfo') // API request csv metadata
                .then(function (response) {
                    self.data.CSVSIZE = response.data[1];
                    self.data.NAME = response.data[0];
                    self.data.ROWS = response.data[2];
                    self.data.COLUMN = response.data[3];
                }).catch(error => {
                console.log(error.response)
            });
        }
    }, mounted() {
        this.getInfos();
    }
});
var vm = new Vue({
    el: '#app',
    delimiters: ["${", "}"]
});


