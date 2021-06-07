document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  
  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  
  // Add event listener to form submit event
  document.querySelector('form').onsubmit = function () {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
    
    console.log(`Sending email to ${recipients}`);

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
      //console.log(result.message);
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
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
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
          tr.innerHTML = `<td>${mail.recipients}</td><td>${mail.subject}</td><td>${mail.timestamp}</td>`;
          tr.addEventListener('click', function() {
              console.log('This element has been clicked!')
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
          tr.innerHTML = `<td>${mail.sender}</td><td>${mail.subject}</td><td>${mail.timestamp}</td>`;
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
          });
          //document.querySelector('h3').after(element);
          tbody.appendChild(tr);
        });
      }
      table.appendChild(tbody);
      document.querySelector('h3').after(table);
      //console.log(emails);

      // ... do something else with emails ...
  });
  
}