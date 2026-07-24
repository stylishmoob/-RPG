import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Login() {

    const[userName,setUserName] = useState("");
    const[password,setPassword] = useState("");
    const[errorMessage,setErrorMessage] = useState("");

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

            setErrorMessage(data.message ?? "ログインに失敗しました");
        }catch(error){
            console.error(error);
            setErrorMessage("サーバーとの通信に失敗しました")
        }
    }

    return (
        <div className="login">
            <h1>ログイン</h1>
            <form onSubmit={(e) => {
                e.preventDefault();
                login()
            }}>
                <input 
                    value={userName}
                    onChange={(e)=>setUserName(e.target.value)}
                    required
                />
                <input 
                    type="password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                    required
                />
                <button type="submit">
                    ログイン
                </button>
            </form>

            {errorMessage && (
                <p className="error-message" >{errorMessage}</p>
            )}

            <div className="links">
                <Link to="/register">新規登録</Link>    
            </div>
        </div> 
    )
}

export default Login;