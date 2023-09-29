const modal = document.getElementById('deleteModal');
modal.addEventListener('show.bs.modal', function (event) {
    this.querySelector('form').action = 
        event.relatedTarget.dataset.url; 
    this.querySelector('.delete-book-title').textContent =
        event.relatedTarget.dataset.title;
    console.log(event.relatedTarget.dataset.url);
});