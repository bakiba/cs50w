document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archive').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email('new','none'));
  
   // Count unread emails
  
  show_unread('inbox');
  show_unread('archive');
  //document.querySelector('#inbox').append(badge);
  
  // By default, load the inbox
  load_mailbox('inbox');
  // clear alerts after 2 sec
  
});

function compose_email(mailId, replyType) {
  
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  if (mailId === 'new') { 
    console.log(`compose_email: ${mailId}`);
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  } else {
    // Fetch email to reply to
    fetch(`/emails/${mailId}`)
    .then(response => response.json())
    .then(email => {
        // Populate fields 
        document.querySelector('#compose-recipients').value = email.sender;
        // If the subject line already begins with Re: , no need to add it again.
        document.querySelector('#compose-subject').value = (email.subject.substr(0, 4) == 'Re: ') ? email.subject : 'Re: ' + email.subject;
        // Prepend each line of original email with > to visualy differentiate original text
        document.querySelector('#compose-body').value = '\r\nOn ' + email.timestamp + ' ' + email.sender + ' wrote: \r\n' + email.body.replace(/^/gm, '>');
        // If reply-all we need to loop though recipients and remove ourselves
        if (replyType === 'reply') {
          document.querySelector('#compose-view h3').innerHTML = 'Reply'; 
        } else {
          document.querySelector('#compose-view h3').innerHTML = 'Reply All';
          const mailbox = document.querySelector('.container h2').innerHTML;
          var replyAllRecipients = [email.sender];
          email.recipients.forEach(recipient => {
            if (recipient === mailbox) {
              return;
            }
            replyAllRecipients.push(recipient);
          });
          document.querySelector('#compose-recipients').value = replyAllRecipients;
        }
    })
    .catch (error => {
      console.error(error);
    });
  }
  
  // Add event listener to form submit event
  document.querySelector('form').onsubmit = function () {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    fetch('/emails', {
      method:'POST',
      body: JSON.stringify({
        recipients: `${recipients}`,
        subject: `${subject}`,
        body: `${body}`
      })
    })
    .then(response => response.json())
    .then(result => {
      if (result.message === undefined) {
        show_message('warning', result.error);
      } else {
        show_message('success', result.message);
        load_mailbox('sent');
      }
    })
    .catch (error => {
      console.error(error);
    });
    return false;
  };
}

function show_message(type, message) {
  const message_div = document.createElement('div');
  message_div.className = `alert alert-${type} alert-dismissable fade show`;
  message_div.innerHTML = `${message} <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>`;
  document.querySelector('hr').after(message_div);
}

function load_mailbox(mailbox) {
  
  
  // Show/update unread mail badge
  show_unread('inbox');
  show_unread('archive');

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#view-email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Load appropriate mailbox (Inbox, Send or Archived)
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      const table = document.createElement('table');
      table.className = 'table table-hover';
      const thead = document.createElement('thead');
      thead.className = 'thead-dark';
      table.appendChild(thead);
      const thFirst = document.createElement('th');
      thFirst.scope = 'col';
      thFirst.innerHTML = 'From';
      const thSecond = document.createElement('th');
      thSecond.scope = 'col';
      thSecond.innerHTML = 'Subject';
      const thThird = document.createElement('th');
      thThird.scope = 'col';
      thThird.innerHTML = 'Received';
      // Append rows to table header
      thead.appendChild(thFirst);
      thead.appendChild(thSecond);
      thead.appendChild(thThird);
      // Append table head to table
      table.appendChild(thead);
      
      // Create table body to later populate in the loop
      const tbody = document.createElement('tbody');
     
      if ( mailbox === 'sent' ) {
        thFirst.innerHTML = 'To';
        thThird.innerHTML = 'Sent';
        emails.forEach(mail => {
          const tr = document.createElement('tr');
          tr.innerHTML = `<td>${mail.recipients}</td><td>${trim_string(mail.subject, 80)}</td><td>${mail.timestamp}</td>`;
          tr.addEventListener('click', function() {
              //console.log('This element has been clicked!')
              view_email(mail.id, mailbox.charAt(0).toUpperCase() + mailbox.slice(1));
          });
          //document.querySelector('h3').after(element);
          tbody.appendChild(tr);
        });
      }
      if ( mailbox === 'inbox' ||  mailbox === 'archive' ) {
        let archive_message = 'Email successfully moved to Archived';
        const btnArchiveTmp = document.createElement('button');
        btnArchiveTmp.className = 'btn btn-sm float-right';
        btnArchiveTmp.type = 'button';
        btnArchiveTmp.setAttribute('data-toggle','tooltip');
        if ( mailbox === 'inbox' ) {
          btnArchiveTmp.innerHTML = '<img src="static/mail/archive.svg" alt="Archive">'
          btnArchiveTmp.title = 'Move to Archive';
          let archive_message = 'Email successfully archived';
        } else {
          btnArchiveTmp.innerHTML = '<img src="static/mail/inbox.svg" alt="Inbox">'
          btnArchiveTmp.title = 'Move to Inbox';
          archive_message = 'Email successfully moved to Inbox';
        }

        emails.forEach(mail => {
          const tr = document.createElement('tr');
          if (mail.read) {
            tr.className = 'read';
          } else {
            tr.className = 'unread';
          }
          tr.innerHTML = `<td>${mail.sender}</td><td>${trim_string(mail.subject, 80)}</td><td>${mail.timestamp}</td>`;
          let btnArchive = btnArchiveTmp.cloneNode(true);
          btnArchive.addEventListener('click', function() {
            //console.log(`Archive button id: ${mail.id} has been clicked!`);
            // Button was clicked, call the PUT and either archive or move to inbox
            fetch(`/emails/${mail.id}`, {
              method: 'PUT',
              body: JSON.stringify({
                  archived: !mail.archived
              })
            })
            .then(response => {
              if (!response.ok) {
                throw new Error('Network response was not ok');
              }
              //console.log('Successfully archived');
              show_message('success', archive_message);
              load_mailbox('inbox');
            })
            .catch (error => {
              console.error(error);
            });
          });
          tr.querySelector('td:last-child').append(btnArchive);
          tr.addEventListener('click', function(event) {
            // We need to see if we clicked Archive button or somewehere inside <TD>
            let target = event.target;
            if (target.tagName != 'TD') return;  
            //console.log(`Email id: ${mail.id} has been clicked!`);
            view_email(mail.id, mailbox.charAt(0).toUpperCase() + mailbox.slice(1));
          });
          //document.querySelector('h3').after(element);
          tbody.appendChild(tr);
        });
      }
      table.appendChild(tbody);
      document.querySelector('h3').after(table);
      //console.log(emails);
  });
  // Clear alerts
  setTimeout(function() {
    $(".alert").alert('close');
  }, 5000); 
}

function view_email(email_id, mailbox){

  document.querySelector('#view-email').innerHTML = '';
  // Show view email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#view-email').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  //// Create email view
  // Create div to hold mailbox name
  const mailbox_div = document.createElement('div');
  mailbox_div.innerHTML = `<span class="badge badge-light">${mailbox}</span>`
  // Create div to hold reply buttons, float to right
  const reply_div = document.createElement('div');
  reply_div.className='float-right';
  // Create reply buttons and add event listeners on click
  const reply_btn = document.createElement('a');
  reply_btn.id='reply';
  reply_btn.setAttribute('data-toggle','tooltip');
  reply_btn.title='Reply';
  reply_btn.href='#';
  const reply_all_btn = document.createElement('a');
  reply_all_btn.id='reply-all';
  reply_all_btn.className='ml-3';
  reply_all_btn.setAttribute('data-toggle','tooltip');
  reply_all_btn.title='Reply All';
  reply_all_btn.href='#';
  reply_btn.innerHTML='<img src="static/mail/Reply-24.png" alt="Replay"></img>'
  reply_all_btn.innerHTML='<img src="static/mail/Reply-All-24.png" alt="Replay All">'
  reply_btn.addEventListener('click',function () {
    compose_email(email_id, 'reply');
  });
  reply_all_btn.addEventListener('click', function () {
    compose_email(email_id, 'reply-all');
  });
  // Append reply buttons to reply div
  reply_div.append(reply_btn);
  reply_div.append(reply_all_btn);

  // Append whole reply div to mailbox div
  mailbox_div.append(reply_div);
  
  // Below mailbox div, we have div that will hold mail details: sender, subject, timestmamp and body
  const mail_details = document.createElement('div');
  
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
      // Print 
      mail_details.innerHTML = `
      <h2 class="display-4 mb-4">${email.subject}</h2>
      <h4 style="display: inline;">${email.sender}</h4><span class="float-right text-muted">${email.timestamp}</span>
      <p class="text-muted"><small>To: ${email.recipients}</small></p>
      <hr>
      <div style="min-height: 200px">
        <p>${email.body.replace(/(?:\r\n|\r|\n)/g, '<br>')}</p>
      </div>
      <hr class="mb-0">
      `
      //console.log(email);
      mark_read(email.id);
  });
  // Append mailbox div and mail details div to main view email div
  document.querySelector('#view-email').append(mailbox_div);
  document.querySelector('#view-email').append(mail_details);
}

function mark_read(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}

function mark_unread(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: false
    })
  })
}

/* function reply_mail(email_id, type) {
  
  compose_email(email_id, type);
} */

function trim_string(subject, length) {
  if ( subject.length > length ) {
    return subject.substr(0,length - 3).substr(0,subject.substr(0,length - 3).lastIndexOf(" ")) + '...';
  } 
  return subject;
}

function show_unread(mailbox) {
  // Load mailbox to count unread messages
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    let unread = 0;
    emails.forEach(mail => {
      if (!mail.read) {
        unread++;
      }
    });
    if (unread > 0) {
      // See if we alredy have badge 
      let badge = document.querySelector(`#${mailbox} span`);
      if (badge) {
        // Update it
        badge.innerHTML = unread;
      } else {
        // If we do not have it, create element, set value and append to button
        badge = document.createElement('span');
        badge.className='badge badge-primary ml-1';
        badge.innerHTML = unread;
        document.querySelector(`#${mailbox}`).append(badge);
      } 
    } else {
      // We need to remove badge is count is 0 and element still exists
      let badge = document.querySelector(`#${mailbox} span`);
      if (badge) {
        badge.remove();
      }
    }
  });
}