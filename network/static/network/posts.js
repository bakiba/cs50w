document.addEventListener('DOMContentLoaded', function () {
    load_posts();
    // Add event listener to form submit event
    const post_form =  document.getElementById('post-form');
    if (post_form) {
        post_form.onsubmit = function () {
            const title = document.querySelector('#post-title').value;
            const content = document.querySelector('#post-content').value;


            fetch('/posts', {
                method: 'POST',
                body: JSON.stringify({
                    title: `${title}`,
                    content: `${content}`
                })
            })
                .then(response => response.json())
                .then(posts => {
                    //console.log('Successfully archived');
                    //show_message('success', "Post successfully created");
                    // clear form
                    document.querySelector('#post-title').value = '';
                    document.querySelector('#post-content').value = '';
                    //clear all posts
                    document.querySelector('#posts-view').innerHTML = '';

                    //load all posts
                    load_posts(posts, null, 1);
                })
                .catch(error => {
                    console.error(error);
                });
            setTimeout(function () {
                $(".alert").alert('close');
            }, 5000);
            return false;
        };
    }

});

function load_posts(data, post_id, page) {
    //console.log(`page was: ${page}`);
    if (page == undefined) { page = 1 }
    if (data != undefined) {
        set_pagination(data.pages.current, data.pages.total)
        data.posts.forEach((post, index) => {
            const post_div = document.createElement('div');
            if (index === 0) {
                post_div.className = 'card mb-1 w-100 anime';
            } else {
                post_div.className = 'card mb-1 w-100';
            }

            post_div.innerHTML = `
                
                <div class="card-body">
                  <h5 class="card-title">${post.title}</h5>
                  <h6 class="card-subtitle mb-2 text-muted">${post.created}</h6>
                  <p class="card-text">${post.content}</p>
                  <a href="#" class="card-link">Like</a>
                </div>
                `;
            document.querySelector('#posts-view').appendChild(post_div)
        });
    } else {
        fetch(`/posts?page=${page}`, {
            method: 'GET'
        })
            .then(response => response.json())
            .then(data => {
                //console.log('Successfully archived');
                //set pagination
                //console.log(data.pages.current);
                set_pagination(data.pages.current, data.pages.total)
                // load posts
                data.posts.forEach(post => {
                    const post_div = document.createElement('div');

                    post_div.className = 'card mb-1 w-100';

                    post_div.innerHTML = `
                    
                    <div class="card-body">
                      <h5 class="card-title">${post.title}</h5>
                      <h6 class="card-subtitle mb-2 text-muted">${post.created}</h6>
                      <p class="card-text">${post.content}</p>
                      <a href="#" class="card-link">Like</a>
                    </div>
                    `;
                    document.querySelector('#posts-view').appendChild(post_div)
                });
            })
            .catch(error => {
                console.error(error);
            });
    }
    //return false;

}

function show_message(type, message) {
    const message_div = document.createElement('div');
    message_div.className = `alert alert-${type} alert-dismissable fade show`;
    message_div.innerHTML = `${message} <button type="button" class="close" data-dismiss="alert" aria-label="Close">
      <span aria-hidden="true">&times;</span>
    </button>`;
    document.querySelector('#new-post').before(message_div);
}

function set_pagination(current, total) {
    //console.log(`Entering set_pagination current:${current}, total:${total}`);
    //clear previous pagination elements
    const pagination = document.querySelector('#pagination');
    pagination.innerHTML = '';
    
    //construct new pagination elements
    // Previous button
    const page_prev = document.createElement('li');
    page_prev.id="page_prev";
    page_prev.className = "page-item";
    page_prev.innerHTML = '<a class="page-link" href="#">Previous</a>'

    // Next button
    const page_next = document.createElement('li');
    page_next.id="page_next";
    page_next.className = "page-item";
    page_next.innerHTML = '<a class="page-link" href="#">Next</a>'
    
    // set prev button disable/enable state
    if (current <= 1) {
        page_prev.classList.add("disabled")
    } else {
        page_prev.classList.remove("disabled")
        page_prev.addEventListener('click', function() { load_posts(null, null, current-1);}, { once: true });
    }
    // set next button disable/enable state
    if (current == total) {
        page_next.classList.add("disabled")
    } else {
        page_next.classList.remove("disabled")
        page_next.addEventListener('click', function () { load_posts(null, null, current+1);}, { once: true });
    }
    pagination.appendChild(page_prev);
    pagination.appendChild(page_next);
    // set inner page buttons
    document.querySelector('#posts-view').innerHTML = '';
    
    //first version - show pagination: for all pages: for (let i = total; i >= 1; i--) {
    //second version - show only max_pages but pagination flows only in one direction: for (let i = Math.max(current , max_pages); i >= Math.max(1, current - max_pages +1 ); i--) {
    // current version - show only max_pages and flow pagination in both directions, does not work nice with even numbers :)
    const max_pages = 5;
    for (let i = Math.min(total, Math.max(max_pages, current + Math.floor(max_pages/2))); i >= Math.min(total-max_pages+1, Math.max(1,current - Math.floor(max_pages/2))); i--) {
        const post_page = document.createElement('li');
        post_page.id = 'page_num'
        if (current == i) {
            post_page.className = "page-item active";
        } else {
            post_page.className = "page-item";
        }

        post_page.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        post_page.addEventListener('click', function () {
            //console.log('This element has been clicked!')
            load_posts(null, null, i);
        });
        page_prev.after(post_page);
    }
}