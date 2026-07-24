import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Register() {
    const[userName,setUserName] = useState("");
    const[password,setPassword] = useState("");
    const[errorMessage,setErrorMessage] = useState("");

    const navigate=useNavigate();

    async function register(){
        try{
            const response = await fetch("/api/register",{
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
                navigate("/login");
                return;
            }

            setErrorMessage(data.message ?? "登録に失敗しました");
        }catch(error){
            console.error(error);
            setErrorMessage("サーバーとの通信に失敗しました")
        }
    }

    return (
        <div className="login">
            <h1>新規登録</h1>
            <form onSubmit={(e) => {
                e.preventDefault();
                register();
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
                    登録
                </button>
            </form>

            {errorMessage && (
                <p className="error-message">{errorMessage}</p>
            )
            }

            <div className="links">
                <Link to="/login">ログイン画面へ</Link>    
            </div>
        </div>  
    )
}

export default Register;