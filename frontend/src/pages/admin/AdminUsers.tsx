import { useEffect,useState } from "react";
import { useNavigate } from "react-router-dom";

import type { AdminUsersDataType } from "../../types/api";
import styles from "../../styles/admin/AdminUsers.module.css";

function AdminUsers(){
    const [adminUsersData,setAdminUsersData] = useState<AdminUsersDataType | null>(null);

    const [editingUserId,setEditingUserId] = useState<string | null>(null);

    const [resettingUserId,setResettingUserId] = useState<string | null>(null);

    const [deletingUserId,setDeletingUserId] = useState<string | null>(null);

    const navigate = useNavigate();

    useEffect(() => {
        fetchAdminUsersData();
    },[navigate]);

    if(!adminUsersData){
        return <div>Loading...</div>;
    }

    const adminUsers = adminUsersData.users;

    async function fetchAdminUsersData(){
        try{
            const response = await fetch("/api/admin/users");
            if(response.status === 401){
                navigate("/login");
                return;
            }
            if(!response.ok){
                throw new Error("データの取得に失敗しました");
            }
            const data: AdminUsersDataType = await response.json();
            setAdminUsersData(data);
        }catch(error){
            console.error(error);
        }
    }

    async function handleIsActiveChange(userId:string,nextIsActive:boolean){
        setEditingUserId(userId);

        try{
            const response = await fetch("/api/admin/users/edit", {
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                },
                body:JSON.stringify({
                    "user_id":userId,
                    "is_active":nextIsActive,
                }),
            });

            if(!response.ok){
                throw new Error("保存に失敗しました");
            }

            setAdminUsersData((currentData) => {
                if(!currentData){
                    return currentData;
                }

                return {
                    ...currentData,
                    users:currentData.users.map((user) => {
                        if(user.id !== userId){
                            return user;
                        }

                        return {
                            ...user,
                            isActive:nextIsActive,
                        };
                    }),
                };
            });
        }catch(error){
            console.error(error);
            await fetchAdminUsersData();
        }finally{
            setEditingUserId(null);
        }
    }

    async function resetUserDataSubmit(userId:string){
        if(userId === "") return;

        const confirmed = window.confirm("このユーザーの進行データを初期化します。アカウント情報は残ります。よろしいですか？");

        if(!confirmed){
            return;
        }

        setResettingUserId(userId);

        try{
            const response = await fetch("/api/reset_user_data", {
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                },
                body:JSON.stringify({
                    "user_id":userId,
                }),
            });

            const data = await response.json();

            if(response.status === 401){
                navigate("/login");
                return;
            }

            if(!response.ok){
                throw new Error(data.message ?? "初期化に失敗しました");
            }

            await fetchAdminUsersData();
        }catch(error){
            console.error(error);
        }finally{
            setResettingUserId(null);
        }
    }

    async function deleteUserSubmit(userId:string,username:string){
        if(userId === "") return;

        const confirmed = window.confirm(`${username} のユーザーアカウントと関連データを削除します。よろしいですか？`);

        if(!confirmed){
            return;
        }

        setDeletingUserId(userId);

        try{
            const response = await fetch("/api/admin/users/delete", {
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                },
                body:JSON.stringify({
                    "user_id":userId,
                }),
            });

            const data = await response.json();

            if(response.status === 401){
                navigate("/login");
                return;
            }

            if(!response.ok){
                throw new Error(data.message ?? "削除に失敗しました");
            }

            await fetchAdminUsersData();
        }catch(error){
            console.error(error);
        }finally{
            setDeletingUserId(null);
        }
    }

    return(
        <div className={styles.page}>
            <h2 className={styles.title}>ユーザー管理</h2>
            <h3>一覧</h3>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>ユーザー名</th>
                        <th>レベル</th>
                        <th>現在の職業</th>
                        <th>管理権限</th>
                        <th>有効化・無効化</th>
                        <th>進行データ</th>
                        <th>ユーザー削除</th>
                    </tr>
                </thead>

                <tbody>
                    {adminUsers.map((user) => {
                        return(
                            <tr key={user.id}>
                                <td>{user.id}</td>
                                <td>{user.username}</td>
                                <td>{user.userLevel}</td>
                                <td>{user.userCurrentJob ?? "未設定"}</td>
                                <td>{user.isAdmin ? "あり" : "なし"}</td>
                                <td>
                                    <select
                                        value={String(user.isActive)}
                                        disabled={editingUserId === user.id || deletingUserId === user.id}
                                        onChange={(e) => {
                                            handleIsActiveChange(user.id,e.target.value === "true");
                                        }}
                                    >
                                        <option value="true">有効</option>
                                        <option value="false">無効</option>
                                    </select>
                                </td>
                                <td>
                                    <button
                                        type="button"
                                        className={styles.resetButton}
                                        disabled={resettingUserId === user.id || deletingUserId === user.id}
                                        onClick={() => {
                                            resetUserDataSubmit(user.id);
                                        }}
                                    >
                                        {resettingUserId === user.id ? "初期化中" : "初期化"}
                                    </button>
                                </td>
                                <td>
                                    <button
                                        type="button"
                                        className={styles.deleteButton}
                                        disabled={deletingUserId === user.id}
                                        onClick={() => {
                                            deleteUserSubmit(user.id,user.username);
                                        }}
                                    >
                                        {deletingUserId === user.id ? "削除中" : "削除"}
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

export default AdminUsers;
