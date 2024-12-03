// import Papa from 'papaparse';

function loadButtons() {
    fetch("out/v2_cluster_single_final/overall/topic1.json")
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse JSON response
        })
        .then(data => {
            var button1_container = document.getElementById("t1-button-container");
            buttons_html = "";
            for (let key in data) {
                buttons_html += "<a href=\"#\" class=\"topic-button\" onclick=\"select_t1(this, '" + key + "')\">" + key + "</a>\n";
            }
            button1_container.innerHTML = buttons_html;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
};

function makeNewButtons(topic1) {
    fetch("out/v2_cluster_single_final/overall/topic2.json")
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse JSON response
        })
        .then(data => {
            var t2_container = document.getElementById("topic2");
            t2_html = "<p class=\"subtitle\">Select a sub-topic to explore:</p>\n<div class=\"topic-grid\" id=\"t2-button-container\">\n";
            
            for (let key in data) {
                if (key === topic1) {
                    t2_data = data[key];
                    for (let t2key in t2_data) {
                        t2_html += "<a href=\"#\" class=\"topic-button\" onclick=\"select_t2(this, '" + key + "', '" + t2key + "')\">" + t2key + "</a>\n";
                    }
                }
            }
            t2_html += "</div>"
            t2_container.innerHTML = t2_html;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
};

function select_t1(button, topic1) {
    const container = button.parentElement;
    container.querySelectorAll('.topic-button').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    makeNewButtons(topic1);
};

function select_t2(button, topic1, topic2) {
    const container = button.parentElement;
    container.querySelectorAll('.topic-button').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    load_results(topic1, topic2);
}

function convert_filename(name) {
    return name.toLowerCase().replace(/\s+/g, '_')
}

function load_results(topic1, topic2) {
    fetch("out/v2_cluster_single_final/csv_out/" + convert_filename(topic1) + "/" + convert_filename(topic2) + ".csv")
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {

            const parsedData = Papa.parse(data, {
                header: true, // Use the first row as headers
                dynamicTyping: true, // Convert numeric and boolean values automatically
                transform: (value, column) => {
                    if (column === 'tat_orig') {
                        repl_list = {"'id': ": "<id>", ", 'article_title': '" : "<article_title>", ", 'article_title': \"" : "<article_title>", "\", 'full_section_title': \"" : "<full_section_title>", "', 'full_section_title': '" : "<full_section_title>", "', 'last_edit_date': '" : "<LED>", "', 'last_edit_date': No" : "<LED_none>", "\", 'last_edit_date': No" : "<LED_none>", "ne, 'num_tokens': " : "<num_tokens_none>", "', 'num_tokens': " : "<num_tokens>", ", 'language': '" : "<language>", "', 'block_type': '" : "<block_type>", "', 'url': '" : "<URL>", "', 'issue_date': '" : "<ISSUE_DATE>", "', 'content': '" : "<CONTENT>", "', 'content': \"" : "<CONTENT>", "'}" : "<CONTENT_END>", "\"}" : "<CONTENT_END>"};
                        new_list = {'<id>': '"id": ', '<article_title>': ', "article_title": "', '<full_section_title>': '", "full_section_title": "', '<LED>': '", "last_edit_date": "', '<LED_none>': '", "last_edit_date": nu', '<num_tokens_none>': 'll, "num_tokens": ', '<num_tokens>': '", "num_tokens": ', '<language>': ', "language": "', '<block_type>': '", "block_type": "', '<URL>': '", "url": "', '<ISSUE_DATE>': '", "issue_date": "', '<CONTENT>': '", "content": "', '<CONTENT_END>': '"}'};
                        for (let key in repl_list) {
                            value = value.replaceAll(key, repl_list[key])
                        }
                        value = value.replaceAll('\\"', '');
                        value = value.replaceAll('"', '');
                        value = value.replaceAll("\\'", '');
                        value = value.replaceAll("'", '');
                        for (let key in new_list) {
                            value = value.replaceAll(key, new_list[key])
                        }
                        console.log(value)
                        return JSON.parse(value);
                    }
                    return value;
                }
            });
            console.log(parsedData.data);

            container = document.getElementById("results");

            parsedData.data.forEach(entry => {
                const div = document.createElement('div');
                div.classList.add("subcontainer");

                // Title
                const title = document.createElement('h2');
                title.innerText = entry.hh;

                // Main content
                const mainContent = document.createElement('p');
                mainContent.innerText = entry.result;

                div.appendChild(title);
                div.appendChild(mainContent);

                // Collapsible items
                ['tat_orig'].forEach(key => {
                    const items = entry[key];
                    if (!items) return
                    items.forEach(item => {
                        const {
                            button,
                            divContent
                        } = createCollapsible(item.document_title || item.article_title, item.content || '');
                        div.appendChild(button);
                        div.appendChild(divContent);
                    });
                });

                container.appendChild(div);
            });
        }).catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
};

function createCollapsible(title, content) {
    const button = document.createElement('button');
    button.className = 'collapsible';
    button.innerText = title;

    const divContent = document.createElement('div');
    divContent.className = 'content';
    divContent.innerHTML = content;

    button.addEventListener('click', function() {
        this.classList.toggle('active1');
        if (divContent.style.display === 'block') {
            divContent.style.display = 'none';
        } else {
            divContent.style.display = 'block';
        }
    });

    return { button, divContent };
}

