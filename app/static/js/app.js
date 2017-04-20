/*
 * Copyright 2016 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the
 * License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * FirebaseUI initialization to be used in a Single Page application context.
 */

// Initialize the FirebaseUI Widget using Firebase.
// var ui = new firebaseui.auth.AuthUI(firebase.auth());
// Keep track of the currently signed in user.
var currentUid = null;

/**
 * Redirects to the FirebaseUI widget.
 */
var signInWithRedirect = function() {
  window.location.assign('/widget');
};


/**
 * Open a popup with the FirebaseUI widget.
 */
var signInWithPopup = function() {
  window.open('/authorize/widget', 'Sign In', 'width=600,height=400');
};


/**
 * Displays the UI for a signed in user.
 * @param {!firebase.User} user
 */
var handleSignedInUser = function(user) {
  currentUid = user.uid;

  document.getElementById('sign-in-with-popup').classList.add('hidden');
  document.getElementById('sign-out').classList.remove('hidden');
  document.getElementById('email').classList.remove('hidden');
};


/**
 * Displays the UI for a signed out user.
 */
var handleSignedOutUser = function() {
  document.getElementById('sign-in-with-popup').classList.remove('hidden');
  document.getElementById('sign-out').classList.add('hidden');
  document.getElementById('email').classList.add('hidden');
};

// Listen to change in auth state so it displays the correct UI for when
// the user is signed in or not.
firebase.auth().onAuthStateChanged(function(user) {
  // The observer is also triggered when the user's token has expired and is
  // automatically refreshed. In that case, the user hasn't changed so we should
  // not update the UI.
  if (user && user.uid == currentUid) {
    return;
  }

  // document.getElementById('loading').style.display = 'none';
  // document.getElementById('loaded').style.display = 'block';

  user ? handleSignedInUser(user) : handleSignedOutUser();
});

/**
 * Deletes the user's account.
 */
var deleteAccount = function() {
  firebase.auth().currentUser.delete().catch(function(error) {
    if (error.code == 'auth/requires-recent-login') {
      // The user's credential is too old. She needs to sign in again.
      firebase.auth().signOut().then(function() {
        // The timeout allows the message to be displayed after the UI has
        // changed to the signed out state.
        setTimeout(function() {
          alert('Please sign in again to delete your account.');
        }, 1);
      });
    }
  });
};


/**
 * Initializes the app.
 */
var initApp = function() {
  // document.getElementById('sign-in-with-redirect').addEventListener('click', signInWithRedirect);
  document.getElementById('sign-in-with-popup').addEventListener('click', signInWithPopup);

  document.getElementById('sign-out').addEventListener('click', function() {
    firebase.auth().signOut();
    window.location.assign('/authorize/sign-out');
  });

  // document.getElementById('delete-account').addEventListener(
  //     'click', function() {
  //       deleteAccount();
  //     });

};

window.addEventListener('load', initApp);
