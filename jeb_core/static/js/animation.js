window.addEventListener('scroll', function(){
    const header = document.getElementById('main-header');
    if (window.innerWidth < 1245) {
        return; 
    }
    if (this.window.scrollY > 100) {
        header.classList.add('scrolled');
        
        
    } else {
        header.classList.remove('scrolled');
    }

});
