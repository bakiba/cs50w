document.addEventListener('DOMContentLoaded', function () {
    
    // Add event listener to form submit event
    const post_form =  document.getElementById('post-form');
    const profile_view =  document.getElementById('profile');
    const following_view =  document.getElementById('following');
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
                    // clear form
                    document.querySelector('#post-title').value = '';
                    document.querySelector('#post-content').value = '';
                    //clear all posts
                    document.querySelector('#posts-view').innerHTML = '';

                    //load all posts
                    load_posts(posts, null, 1,undefined);
                })
                .catch(error => {
                    console.error(error);
                });
            // setTimeout(function () {
            //     $(".alert").alert('close');
            // }, 5000);
            return false;
        };
    }
    // If we are in profile view or following view, load only specific user posts, else load all posts
    if (profile_view || following_view ) {
        load_posts(null, null, 1, UserProfile);        
    } else {
        load_posts();
    }

});
// This function should be re-factored as there is duplication when new post is added, functionality could be done better
function load_posts(data, post_id, page, profile) {
    if (page == undefined) { page = 1 }
    if (data != undefined) {
        set_pagination(data.pages.current, data.pages.total, profile)
        data.posts.forEach((post, index) => {
            const post_div = document.createElement('div');
            // If this is newly added post it will be animated
            if (index === 0) {
                post_div.className = 'card mb-1 w-100 anime';
            } else {
                post_div.className = 'card mb-1 w-100';
            }
            // this part is repeated again arround lines 98/99, consider re-factoring
            var likeBtnTxt = 'Like';
            var post_content = post.content.replace(/\n/g, "<br>");
            if (data.likes.includes(post.id)) {
                likeBtnTxt = 'Unlike';
            }
            // If user is author of the post, we need to enable edit post link
            var editPostLink = '';
            if (AuthenticatedUser != 'AnonymousUser' && AuthenticatedUser == post.user) {
                editPostLink = `<a id="edit_post_${post.id}" href="#/" class="card-link" data-toggle="tooltip" title="Edit post"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill" viewBox="0 0 16 16">
                <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
                </svg></a> `
            }
            post_div.innerHTML = `
            <div class="card-body">
            <h5 class="card-title" style="display: inline;">${editPostLink}${post.title}</h5> <span class="float-right text-muted small">${post.created}</span>
              <h6 class="card-subtitle mb-2 text-muted">by <a href="/profile/${post.user}">${post.user}</a></h6>
              <p class="card-text">${post_content}</p>
              
                <button id="like_btn_${post.id}" type="button" class="btn btn-outline-primary btn-sm">
                    Like <span class="badge badge-light">${post.likes}</span>
                </button>
              <!--<a href="#" class="card-link"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
            </svg></a>-->
            </div>
                `;
            document.querySelector('#posts-view').appendChild(post_div)
            if (AuthenticatedUser != 'AnonymousUser' && AuthenticatedUser != post.user) {
                document.querySelector(`#like_btn_${post.id}`).addEventListener('click', function() {
                    
                    fetch(`/like/${post.id}`, {
                        method: 'PUT'
                    })
                    .then(response => response.json())
                    .then(post => {
                        // Set the new like count
                        this.innerHTML=`${data.likeBtnTxt} <span class="badge badge-light">${post.likes}</span>`
                    })
                    .catch (error => {
                        console.error(error);
                    });
                });
            } else {
                document.querySelector(`#like_btn_${post.id}`).setAttribute('disabled', true);
            }
            editPostHandler(post_div, post.id)
        });
    } else {
        fetch(`/posts?page=${page}&profile=${profile}`, {
            method: 'GET'
        })
            .then(response => response.json())
            .then(data => {
                //set pagination
                set_pagination(data.pages.current, data.pages.total, profile)
                // load posts
                data.posts.forEach(post => {
                    const post_div = document.createElement('div');
                    post_div.className = 'card mb-1 w-100';
                    var likeBtnTxt = 'Like';
                    // Replace nl with <br> to keep line breaks visual
                    var post_content = post.content.replace(/\n/g, "<br>");
                    // If user liked this post, change button text to "Unlike"
                    if (data.likes.includes(post.id)) {
                        likeBtnTxt = 'Unlike';
                    }
                    // If user is author of the post, we need to enable edit post link
                    var editPostLink = '';
                    if (AuthenticatedUser != 'AnonymousUser' && AuthenticatedUser == post.user) {
                        editPostLink = `<a id="edit_post_${post.id}" href="#/" class="card-link" data-toggle="tooltip" title="Edit post"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill" viewBox="0 0 16 16">
                        <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
                        </svg></a> `
                    }
                    // Structure of the post with all the elements
                    post_div.innerHTML = `
                    <div class="card-body">
                    <h5 class="card-title" style="display: inline;">${editPostLink}${post.title}</h5> 
                    <span id="post_created" class="float-right text-muted small">${post.created}</span>
                     
                      <h6 class="card-subtitle mt-1 mb-2 text-muted">by <a href="/profile/${post.user}">${post.user}</a></h6>
                      <p class="card-text">${post_content}</p>
                      
                        <button id="like_btn_${post.id}" type="button" class="btn btn-outline-primary btn-sm">
                            ${likeBtnTxt} <span class="badge badge-light">${post.likes}</span>
                        </button>
                      <!--<a href="#" class="card-link"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16">
                      <path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
                    </svg></a>-->
                    </div>
                    `;
                    // Append element to post div
                    document.querySelector('#posts-view').appendChild(post_div);
                    // Enable like button only for authenticated users and not on self posts
                    if (AuthenticatedUser != 'AnonymousUser' && AuthenticatedUser != post.user) {
                        document.querySelector(`#like_btn_${post.id}`).addEventListener('click', function() {
                            
                            fetch(`/like/${post.id}`, {
                                method: 'PUT'
                            })
                            .then(response => response.json())
                            .then(data => {
                                // Set the new like count
                                this.innerHTML=`${data.likeBtnTxt} <span class="badge badge-light">${data.likes}</span>`
                            })
                            .catch (error => {
                                console.error(error);
                            });
                        });
                    } else {
                        document.querySelector(`#like_btn_${post.id}`).setAttribute('disabled', true);
                    }
                    // Handle post editing logic in separate function
                    editPostHandler(post_div, post.id)
                });
            })
            .catch(error => {
                console.error(error);
            });
    }
    //return false;

}

// Function to show banner messages, currently not used
// function show_message(type, message) {
//     const message_div = document.createElement('div');
//     message_div.className = `alert alert-${type} alert-dismissable fade show`;
//     message_div.innerHTML = `${message} <button type="button" class="close" data-dismiss="alert" aria-label="Close">
//       <span aria-hidden="true">&times;</span>
//     </button>`;
//     document.querySelector('#new-post').before(message_div);
// }

function set_pagination(current, total, profile) {
    //clear previous pagination elements
    const pagination = document.querySelector('#pagination');
    pagination.innerHTML = '';
    
    //construct new pagination elements
    // Previous button
    const page_prev = document.createElement('li');
    page_prev.id="page_prev";
    page_prev.className = "page-item";
    page_prev.innerHTML = '<a class="page-link" href="#/">Previous</a>'

    // Next button
    const page_next = document.createElement('li');
    page_next.id="page_next";
    page_next.className = "page-item";
    page_next.innerHTML = '<a class="page-link" href="#/">Next</a>'
    
    // set prev button disable/enable state
    if (current <= 1) {
        page_prev.classList.add("disabled")
    } else {
        page_prev.classList.remove("disabled")
        page_prev.addEventListener('click', function() { load_posts(null, null, current-1, profile);}, { once: true });
    }
    // set next button disable/enable state
    if (current == total) {
        page_next.classList.add("disabled")
    } else {
        page_next.classList.remove("disabled")
        page_next.addEventListener('click', function () { load_posts(null, null, current+1, profile);}, { once: true });
    }
    pagination.appendChild(page_prev);
    pagination.appendChild(page_next);
    // set inner page buttons
    document.querySelector('#posts-view').innerHTML = '';
    
    //first version - show pagination: for all pages: for (let i = total; i >= 1; i--) {
    //second version - show only max_pages but pagination flows only in one direction: for (let i = Math.max(current , max_pages); i >= Math.max(1, current - max_pages +1 ); i--) {
    // current version - show only max_pages and flow pagination in both directions, does not work nice with even numbers :)
    const max_pages = (total < 5) ? total : 5;
    for (let i = Math.min(total, Math.max(max_pages, current + Math.floor(max_pages/2))); i >= Math.min(total-max_pages+1, Math.max(1,current - Math.floor(max_pages/2))); i--) {
        const post_page = document.createElement('li');
        post_page.id = 'page_num'
        if (current == i) {
            post_page.className = "page-item active";
        } else {
            post_page.className = "page-item";
        }

        post_page.innerHTML = `<a class="page-link" href="#/">${i}</a>`;
        post_page.addEventListener('click', function () {
            load_posts(null, null, i, profile);
        });
        page_prev.after(post_page);
    }
}

function editPostHandler(post_div, post_id) {
    var editPost = document.querySelector(`#edit_post_${post_id}`);
    if (editPost !== null) {
        editPost.addEventListener('click', function() {
            // Get the post title and content
            post_title = post_div.querySelector('div h5');
            post_content = post_div.querySelector('p.card-text');
            like_btn = post_div.querySelector(`#like_btn_${post_id}`);

            // Create the input elements
            inputTitle = document.createElement("input");
            inputTitle.type = "text";
            inputTitle.value = post_title.textContent.trim();
            inputTitle.className = "form-control w-75";
            inputTitle.style.display = "inline";
            
            inputContent = document.createElement("textarea");
            inputContent.type = "textarea";
            inputContent.className = "form-control mb-1";
            // Trim whitespaces and replace <br> with nl as post content will be displayed in textarea
            inputContent.value = post_content.innerHTML.trim().replace(/<br\s*[\/]?>/gi, "\n");
            
            // Create the save and cancel buttons
            saveBtn = document.createElement("button");
            cancelBtn = document.createElement("button");
            saveBtn.className="btn btn-outline-primary mr-1";
            cancelBtn.className="btn btn-outline-primary";
            saveBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16">
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path>
                    <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"></path>
                </svg>
            `;
            cancelBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle" viewBox="0 0 16 16">
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                    <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                </svg>
            `;
            // Replace the title and content
            post_title.replaceWith(inputTitle);
            post_content.replaceWith(inputContent);
            like_btn.replaceWith(saveBtn, cancelBtn)

            // Set the height of the textarea to match the size of text
            inputContent.style.height = inputContent.scrollHeight + "px";
            inputContent.style.overflowY = "hidden";
            inputTitle.focus();
            
            // Add save button onclick functionality
            saveBtn.addEventListener('click', function() {
                fetch(`/edit/${post_id}`, {
                    method: 'POST',
                    body: JSON.stringify({
                        title: `${inputTitle.value}`,
                        content: `${inputContent.value}`
                    })
                })
                .then(response => response.json())
                .then(data => {
                    
                    // We need to update title with new text
                    // Setting nodeValue via textContent or innerText replaces all child nodes, element.lastChild.nodeValue will handle this
                    post_title.lastChild.nodeValue = " " + data.title;
                    // Replace nl with <br> to keep the line breaks visible
                    post_content.innerHTML = data.content.replace(/\n/g, "<br>");

                    // Swap elements
                    inputTitle.replaceWith(post_title);
                    inputContent.replaceWith(post_content);
                    
                    // Bring back the like button
                    cancelBtn.replaceWith(like_btn);
                    // Remove save button
                    this.remove();
                    

                })
                .catch (error => {
                    console.error(error);
                });                
            });
            // Cancel button functionlity, basically revert input fields to previous elements
            cancelBtn.addEventListener('click', function() {
                inputTitle.replaceWith(post_title);
                inputContent.replaceWith(post_content);
                saveBtn.replaceWith(like_btn);
                this.remove();
            });

        });
    }
}