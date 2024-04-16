<!-- ResetPasswordForm.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { createEventDispatcher } from 'svelte';

  let email = '';
  let code = '';
  let newPassword = '';
  let errorMessage = '';

  const dispatch = createEventDispatcher();

  async function handleSubmit() {
    try {
      const response = await fetch('/reset_password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, code, new_password: newPassword })
      });

      if (response.ok) {
        // Reset form and display success message
        email = '';
        code = '';
        newPassword = '';
        errorMessage = '';
        alert('Password reset successful!');
      } else {
        // Display error message
        const errorData = await response.json();
        errorMessage = errorData.message;
      }
    } catch (error) {
      console.error('Error:', error);
      errorMessage = 'An error occurred. Please try again later.';
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <label>
    Email:
    <input type="email" bind:value={email} required />
  </label>
  <label>
    Reset Code:
    <input type="text" bind:value={code} required />
  </label>
  <label>
    New Password:
    <input type="password" bind:value={newPassword} required />
  </label>
  <button type="submit">Reset Password</button>
  {errorMessage && <p style="color: red;">{errorMessage}</p>}
</form>

