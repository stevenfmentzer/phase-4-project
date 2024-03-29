import React, { useState } from "react";

function LoginForm({ user, onLogin, setEnterSite }){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
  
    function handleSubmit(e) {
      e.preventDefault();
      setIsLoading(true);
      fetch('http://localhost:5555/login', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password })
      })
      .then((r) => {
        setIsLoading(false);
        if (r.ok) {
          r.json().then((user) => {
            localStorage.setItem('authToken', user.token); // Store the token in localStorage
            onLogin(user);
            setEnterSite(true);
          });
        }
      });
    }
    

    return(
        <form onSubmit={handleSubmit}>
        <input type="text" id="username" placeholder="username" autoComplete="off" value={username} onChange={(e) => setUsername(e.target.value)}/>
        <input type="text" id="password" placeholder="password" autoComplete="off" value={password} onChange={(e) => setPassword(e.target.value)}/>
        <button variant="fill" color="primary" type="submit">
          {isLoading ? "Loading..." : "Login"}
        </button>
        </form>

    )
}

export default LoginForm