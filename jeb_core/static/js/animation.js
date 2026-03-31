window.addEventListener('scroll', function(){
    const header = document.getElementById('main-header');
  
    if (this.window.scrollY > 100) {
        header.classList.add('scrolled');
        
        
    } else {
        header.classList.remove('scrolled');
    }

});
