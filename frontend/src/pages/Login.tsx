import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Login() {

    const[userName,setUserName] = useState("");
    const[password,setPassword] = useState("");

    const navigate=useNavigate();

    async function login(){
        try{
            const response = await fetch("/api/login",{
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                },
                body: JSON.stringify({
                    user_name:userName,
                    password:password,
                }),
            });

            const data = await response.json();

            if(response.ok && data.success){
                navigate("/");
                return;
            }

            alert(data.message ?? "ログインに失敗しました");
        }catch(error){
            console.error(error);
            alert("サーバーとの通信に失敗しました")
        }
    }

    return (
            <div className="login">
                <h1>ログイン</h1>
                <input 
                    value={userName}
                    onChange={(e)=>setUserName(e.target.value)}
                />
                <input 
                    type="password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                />

                <button onClick={login}>
                    ログイン
                </button>
            

                <div className="links">
                    <Link to="/register"></Link>    
                </div>
            </div>  
    );
}

export default Login;