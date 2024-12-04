 // Import the functions you need from the SDKs you need
 import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js";
 import { getAuth, signInWithPopup, signInWithEmailAndPassword, GoogleAuthProvider,FacebookAuthProvider } from "https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js";

 //configuración de Firebase
 const firebaseConfig = {
     apiKey: "AIzaSyBUm-K6-xIEQoElk-qqSgCnsEiKDf-Sp0k",
     authDomain: "fir-autentication-68c33.firebaseapp.com",
     projectId: "fir-autentication-68c33",
     storageBucket: "fir-autentication-68c33.appspot.com",
     messagingSenderId: "838977190328",
     appId: "1:838977190328:web:05f82a0479b84bbb79b74d",
     measurementId: "G-96DKR8N2XJ"
 };

 // Iniciar Firebase
 const app = initializeApp(firebaseConfig);
 const auth = getAuth(app);

 
 //inicio de sesion login

 /*const signinForm = document.querySelector('#login-form');

 signinForm.addEventListener('submit', e => {
     e.preventDefault();
     const email = document.querySelector('#login-email').value;
     const password = document.querySelector('#login-password').value;

     signInWithEmailAndPassword(auth, email, password)
         .then(userCredential => {
             signinForm.reset();
             console.log('Inicio de sesión exitoso:', userCredential.user);

             alert('inicio de sesion exitoso');
             window.location.href = 'index1.html';
         })
         .catch(error => {
             console.error('Error en el inicio de sesión:', error);
             alert('inicio de sesion fallido, credenciales incorrectas');
         });
 });*/

// autenticacion con google

 // proveedor de Google
 const provider = new GoogleAuthProvider();

 const googleButton = document.querySelector('#googleLogin');
 googleButton.addEventListener('click', e => {
     e.preventDefault();
     signInWithPopup(auth, provider)
         .then((result) => {
             console.log('Inicio de sesión con Google exitoso');
             const user = result.user;
             console.log(user);

             window.location.href = 'inicio.html';
         })
         .catch((error) => {
             console.error('Error durante la autenticación con Google', error);
         });
 });
