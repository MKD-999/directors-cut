<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  let vault = $state([]);
  let loading = $state(false);

  onMount(() => {
    const saved = localStorage.getItem("vault");
    if (saved) vault = JSON.parse(saved);
  });

  function removeFromVault(title) {
    vault = vault.filter(m => m.title !== title);
    localStorage.setItem("vault", JSON.stringify(vault));
  }

  function clearVault() {
    if (confirm("Are you sure you want to reset your collection?")) {
      vault = [];
      localStorage.removeItem("vault");
    }
  }

  async function getRecs() {
    if (vault.length === 0) return;
    loading = true;
    
    const movieData = {};
    vault.forEach(m => { 
      movieData[m.title] = m.user_rating || 5; 
    });

    try {
      const res = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ movies: movieData })
      });
      
      if (!res.ok) throw new Error("API Error");
      
      const data = await res.json();
      localStorage.setItem("latest_recs", JSON.stringify(data));
      goto("/recommendations");
      
    } catch (e) { 
      console.error(e); 
    } finally { 
      loading = false; 
    }
  }
</script>
<svelte:head>
  <title>Director's Cut | The Collection</title>
</svelte:head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,900&family=Poppins:wght@400;500&family=Raleway:wght@800&display=swap');
  
  :global(body) { background: #000; margin: 0; color: white; font-family: 'Poppins', sans-serif; }
  
  .visual-sans { font-family: 'Inter', sans-serif; font-weight: 900; text-transform: uppercase; letter-spacing: -0.02em; }
  
  /* Navigation & Utility Buttons */
  nav { display: flex; justify-content: space-between; padding: 30px 6%; align-items: center; border-bottom: 1px solid #111; }
  
  .nav-btn {
    background: none; border: 1px solid #222; color: #555; 
    padding: 8px 16px; border-radius: 4px; cursor: pointer; 
    font-weight: 800; font-size: 0.6rem; text-transform: uppercase; 
    font-family: 'Inter'; transition: 0.3s;
  }
  .nav-btn:hover { border-color: #fff; color: #fff; }
  .clear-btn:hover { border-color: #c4302b; color: #c4302b; }

  /* Vault Cards */
  .v-grid { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-top: 50px; }
  .v-card { width: 150px; position: relative; border-radius: 6px; overflow: hidden; border: 1px solid #111; background: #050505; }
  .v-card img { width: 100%; aspect-ratio: 2/3; object-fit: cover; filter: grayscale(1); transition: 0.5s; }
  .v-card:hover img { filter: grayscale(0); }
  
  .remove-btn { 
    position: absolute; top: 8px; right: 8px; background: rgba(0,0,0,0.8); 
    color: white; border: none; border-radius: 50%; width: 24px; height: 24px; 
    cursor: pointer; z-index: 10; font-size: 10px; display: flex; align-items: center; justify-content: center;
  }

  /* Main Action Button */
  .action-btn {
    margin-top: 60px; padding: 22px 50px; 
    background: transparent; color: #ffffff; 
    border: 2px solid #333; border-radius: 100px; 
    font-weight: 900; cursor: pointer; text-transform: uppercase; 
    letter-spacing: 3px; font-family: 'Inter'; 
    transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 320px; /* Prevents button jump when text changes */
  }
  
  .action-btn:hover:not(:disabled) { 
    background: #ffffff;
    color: #000000;
    border-color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(255, 255, 255, 0.4); 
  }
  
  .action-btn:active:not(:disabled) {
    transform: translateY(1px);
  }

  /* Fixed the 'gray thing' visibility */
  .action-btn:disabled { 
    opacity: 0.5; /* Increased from 0.1 so text is visible */
    cursor: not-allowed;
    border-color: #222;
    color: #888; /* Soft gray text while loading */
  }

  /* Ensure the span doesn't inherit weird positioning */
  .action-btn span {
    display: block;
    width: 100%;
  }
</style>

<main>
  <nav>
    <h1 onclick={() => goto("/")} class="visual-sans" style="cursor:pointer; font-size:1rem; letter-spacing:0.3em; margin:0;">DIRECTOR’S CUT</h1>
    <div style="display: flex; gap: 12px;">
      <button class="nav-btn clear-btn" onclick={clearVault}>Clear Collection</button>
      <button class="nav-btn" onclick={() => goto("/")}>Back to Search</button>
    </div>
  </nav>

  <section style="padding:80px 6%; text-align:center;">
    <h2 class="visual-sans" style="font-size:4.5rem; margin:0; line-height:0.9;">The Collection</h2>
    <p style="font-family:'Raleway'; color:#c4302b; font-weight:800; text-transform:uppercase; letter-spacing:4px; font-size:0.9rem; margin-top:20px;">A history of your preferences.</p>

    <div class="v-grid">
      {#each vault as movie}
        <div class="v-card">
          <button class="remove-btn" onclick={() => removeFromVault(movie.title)}>✕</button>
          <img src={movie.poster} alt="" />
          <div style="padding:10px; color:#ffbd2e; text-align:center; font-family:'Inter'; font-size:0.75rem;">
            {"★".repeat(movie.user_rating)}
          </div>
        </div>
      {/each}
    </div>

    <button onclick={getRecs} disabled={loading || vault.length === 0} class="action-btn">
      {#if loading}
        <span style="letter-spacing: 1px;">Developing the shortlist...</span>
      {:else}
        Run the Final Cut
      {/if}
    </button>
  </section>
</main>