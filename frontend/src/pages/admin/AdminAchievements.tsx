import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";

import type { AchievementsType,AchievementsDataType } from "../../types/api";


function AdminAchievements(){
    const [AchievementsData,setAchievementsData] =useState<AchievementsDataType | null>(null);

    const navigate = useNavigate()

    const [addCategoryId,setAddCategoryId] = useState<string>("");

    const [addHours,setAddHours] = useState<number | null>(null)

    const [addAchievementName,setAddAchievementName] = useState<string>("")

    const [addTitleName,setAddTitleName] =useState<string>("");

    const [editCategoryId,setEditCategoryId]=useState<string>("");

    const [editHours,setEditHours] = useState<number | null>(null)

    const [editAchievementName,setEditAchievementName] = useState<string>("");

    const [editTitleName,setEditTitleName] =useState<string>("");

    const [editAchievementIsActive,setEditAchievementIsActive] = useState<boolean>(true);

    const [editingId,setEditingId] = useState<string>("");

    const [csvFile,setCsvFile] = useState<File | null>(null);

     useEffect(() => {
            fetchAchievementsData();
        },[navigate]);

    if (!AchievementsData){
        return <div>Loading...</div>;
    }

    const achievements = AchievementsData.achievements

    const masterCategories = AchievementsData.mastercategories


    async function fetchAchievementsData(){
                try{
                    const response = await fetch("/api/admin/achievements");
                    if(response.status === 401){
                        navigate("/login");
                        return;
                    }
                    if(!response.ok){
                        throw new Error("データの取得に失敗しました");
                    }
                    const data: AchievementsDataType = await response.json();
                    setAchievementsData(data);
                } catch (error){
                    console.error(error);
                }
            }

    async function addAchievementSubmit(e: React.FormEvent<HTMLElement>){
        e.preventDefault();

        try{
            await handleAdd();
            await fetchAchievementsData();

            setAddCategoryId("");
            setAddHours(null);
            setAddAchievementName("");
            setAddTitleName("");
        }catch(error){
            console.error(error);
        }
    }

     async function handleAdd(){
        const response = await fetch("/api/admin/achievements/add", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "category_id":addCategoryId,
                "required_hours":addHours,
                "achievement_name":addAchievementName,
                "title_name":addTitleName,
            }),
        });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function editAchievementSubmit(){
        if(editingId === "" ||
            editCategoryId === "" ||
            editHours === null 
        ) return;
       
        try{
            await handleEdit(editingId,editCategoryId,editHours,editAchievementName,editTitleName,editAchievementIsActive);
            await fetchAchievementsData();

            setEditingId("");
            setEditHours(null);
            setEditAchievementName("");
            setEditTitleName("");
            setEditAchievementIsActive(true);
        }catch(error){
            console.error(error);
        }
    }

     async function handleEdit(
        editingId:string,
        editCategoryId:string,
        editHours:number,
        editAchievementName:string,
        editTitleName:string,
        editAchievementIsActive:boolean
        )
        {
        const response = await fetch("/api/admin/categories/edit", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "achievement_id":editingId,
                "category_id":editCategoryId,
                "required_hours":editHours,
                "achievement_name":editAchievementName,
                "title_name":editTitleName,
                "Achievement_is_active":editAchievementIsActive,
        }),
    });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    function startEditing(achievement:AchievementsType){
            setEditingId(achievement.id);
            setEditCategoryId(achievement.category_id);
            setEditHours(achievement.required_hours);
            setEditAchievementName(achievement.achievement_name); 
            setEditTitleName(achievement.title_name);
            setEditAchievementIsActive(achievement.is_active);
        }

    async function importCsvSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        if (!csvFile) return;

        try{
            const formData = new FormData();
            formData.append("file", csvFile);

            const response = await fetch("/api/admin/achivements/import", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message);
            }
            await fetchAchievementsData();
            setCsvFile(null);
        }catch(error){
            console.error(error);
        }
    }

    return (
        <div>
            <h2>勲章・称号 管理</h2>

            <form onSubmit={addAchievementSubmit}>
                <select 
                    value={addCategoryId}
                    onChange={(e) => setAddCategoryId(e.target.value)}>

                    {masterCategories.map((category) => {
                        return(
                            <option value={category.id}>
                                {category.id} : {category.name}
                            </option>
                        )          
                    })}
                </select>
                <input 
                    type="number" 
                    value={addHours ?? ""} 
                    placeholder="必要時間(h)"
                    onChange={(e) =>setAddHours(e.target.value === "" ? null : Number(e.target.value))} 
                    required
                />
                <input 
                    type="text" 
                    value={addAchievementName} 
                    placeholder="アチーブメント名"
                    onChange={(e) =>setAddAchievementName(e.target.value)} 
                    required
                />
                <input 
                    type="text" 
                    value={addTitleName} 
                    placeholder="称号名" 
                    onChange={(e) =>setAddTitleName(e.target.value)}
                    required
                />
                <button type="submit">追加</button>
            </form>

            <form onSubmit={importCsvSubmit}>
                <input
                    type="file"
                    accept=".csv,text/csv"
                    onChange={(e) => {
                        setCsvFile(e.target.files?.[0] ?? null);
                    }}
                />
                <button type="submit" disabled={!csvFile}>
                    CSV一括追加
                </button>
            </form>

            <table>
                <tr>
                    <th>ID</th>
                    <th>必要カテゴリー名</th>
                    <th>必要時間/h</th>
                    <th>アチーブメント名</th>
                    <th>称号名</th>
                    <th>有効化・無効化</th>
                </tr>

                {achievements.map((achievement) => {
                    return(
                        <tr key={achievement.id}
                            className={editingId === achievement.id ? "editing-row" :""}
                         >
                            <td>{achievement.id}</td>
                            <td>
                                <div>{achievement.category_name}</div>
                                <select 
                                    value={editCategoryId}
                                    disabled={editingId !== achievement.id}
                                    onChange={(e) => setEditCategoryId(e.target.value)}>

                                    {masterCategories.map((category) => {
                                        return(
                                            <option value={category.id}>
                                            {category.id} : {category.name}
                                            </option>
                                        )          
                                    })}
                                </select>
                            </td>
                            <td>
                                <div>{achievement.required_hours}</div>
                                <input
                                    type="text"
                                    value={editHours ?? ""}
                                    disabled={editingId !== achievement.id}
                                    placeholder="時間/h" 
                                    onChange={(e) => setEditHours(e.target.value === "" ? null: Number(e.target.value))}/>
                            </td>
                                    
                            <td>{achievement.achievement_name}</td>
                                <input 
                                    type="text" 
                                    value={editAchievementName}
                                    disabled={editingId !== achievement.id}
                                    placeholder="勲章名" 
                                    onChange={(e) => setEditAchievementName(e.target.value)}
                                />
                            <td>{achievement.title_name}</td>
                                <input 
                                    type="text" 
                                    value={editTitleName}
                                    disabled={editingId !== achievement.id}
                                    placeholder="称号名" 
                                    onChange={(e) => setEditTitleName(e.target.value)}
                                />
                            <td>
                                <select
                                value={editingId === achievement.id 
                                    ? String(editAchievementIsActive) 
                                    : String(achievement.is_active)
                                }
                                disabled={editingId !== achievement.id}
                                onChange={(e) => 
                                    setEditAchievementIsActive(
                                        e.target.value === "true")}
                                >
                                    <option value="true">有効</option>
                                    <option value="false">無効</option> 
                                </select>   
                            </td>
                            <td>
                                <button
                                    type="button"
                                    onClick={() =>{                                  
                                        startEditing(achievement)
                                    } }>
                                    編集
                                </button>
                                <button 
                                    type="button"
                                    disabled={editingId !== achievement.id}
                                    onClick={() =>{
                                        editAchievementSubmit()
                                    }}>
                                    変更
                                </button>
                            </td>
                        </tr>
                    )
                })}
            </table>
        </div>
    )
}
export default AdminAchievements;