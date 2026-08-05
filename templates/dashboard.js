async function login() {

    const res = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: document.getElementById("user").value,
            password: document.getElementById("pass").value
        })
    });

    const data = await res.json();

    // save token in browser memory
    localStorage.setItem("token", data.token);

    // show message
    document.getElementById("output").innerText =
        "Logged in as " + data.role;
}