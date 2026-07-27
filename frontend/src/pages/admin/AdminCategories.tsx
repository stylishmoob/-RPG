import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";

import type { MasterCategoriesType,MasterCategoriesDataType } from "../../types/api";
import styles from "../../styles/admin/AdminCategories.module.css";

function AdminCategories(){
    const [MasterCategoriesData,setMasterCategoriesData] = useState<MasterCategoriesDataType | null>(null); 

    const navigate = useNavigate()

    const [addCategoryName,setAddCategoryName] = useState<string>("");

    const [editCategoryName,setEditCategoryName] = useState<string>("");

    const [editCategoryIsActive,setEditCategoryIsActive] = useState<boolean>(true);

    const [editingId,setEditingId] = useState<string>("");

    const [csvFile,setCsvFile] = useState<File | null>(null);

    useEffect(() => {
            fetchMasterCategoriesData();
        },[navigate]);

    if (!MasterCategoriesData){
        return <div>Loading...</div>;
    }

    const MasterCategories = MasterCategoriesData.MasterCategories

    async function fetchMasterCategoriesData(){
            try{
                const response = await fetch("/api/admin/categories");
                if(response.status === 401){
                    navigate("/login");
                    return;
                }
                if(!response.ok){
                    throw new Error("データの取得に失敗しました");
                }
                const data: MasterCategoriesDataType = await response.json();
                setMasterCategoriesData(data);
            } catch (error){
                console.error(error);
            }
        }

    async function addHandleSubmit(e: React.FormEvent<HTMLElement>){
        e.preventDefault();

        if(
            addCategoryName === ""
        ) return;

        try{
            await handleAdd(addCategoryName);
            setAddCategoryName("");
            await fetchMasterCategoriesData();
        }catch(error){
            console.error(error);
        }
    }

    async function handleAdd(addCategoryName:string){
        const response = await fetch("/api/admin/categories/add", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "category_name":addCategoryName,
            }),
        });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function editCategorySubmit(){
        if(
            editingId === "" ||
            editCategoryName === ""
        ) return;
       
        try{
            await handleEdit(editingId,editCategoryName,editCategoryIsActive);
            await fetchMasterCategoriesData();

            setEditingId("");
            setEditCategoryName("");
            setEditCategoryIsActive(true);
        }catch(error){
            console.error(error);
        }
    }

     async function handleEdit(
        editingId:string,
        editCategoryName:string,
        editCategoryIsActive:boolean
        )
        {
        const response = await fetch("/api/admin/categories/edit", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "category_id":editingId,
                "category_name":editCategoryName,
                "is_active":editCategoryIsActive,
        }),
    });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    function startEditing(category:MasterCategoriesType){
        setEditingId(category.id);
        setEditCategoryName(category.name); 
        setEditCategoryIsActive(category.is_active);
    }

     async function importCsvSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        if (!csvFile) return;

        try{
            const formData = new FormData();
            formData.append("file", csvFile);

            const response = await fetch("/api/admin/categories/import", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message);
            }
            await fetchMasterCategoriesData();
            setCsvFile(null);
        }catch(error){
            console.error(error);
        }
    }
    

    return(
        <div className={styles.page}>
            <h2 className={styles.title}>カテゴリー管理</h2>
            <h3>追加</h3>
            <form className={styles.form} onSubmit={addHandleSubmit}>
                <input 
                    type="text" 
                    value={addCategoryName} 
                    placeholder="カテゴリー名" 
                    onChange={(e) => setAddCategoryName(e.target.value)}
                    required
                />
                <button type="submit">追加</button>
            </form>
            <h3>csv追加</h3>
            <form className={styles.form} onSubmit={importCsvSubmit}>
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
            <h3>編集</h3>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>カテゴリー名</th>
                        <th>有効化・無効化</th>
                        <th>編集・変更</th>
                    </tr>
                </thead>

                <tbody>
                    {MasterCategories.map((category) => {

                    return(
                        <tr key={category.id}
                            className={editingId === category.id ? styles.editingRow : ""}
                        >
                            <td>{category.id}</td>
                            <td>
                                <div className={styles.field}>
                                    <span>{category.name}</span>
                                    <input
                                        type="text"
                                        value={editingId === category.id ? editCategoryName : category.name}
                                        disabled={editingId !== category.id}
                                        placeholder="カテゴリー名"
                                        onChange={(e) => setEditCategoryName(e.target.value)}
                                    />
                                </div>
                            </td>
                            <td>
                                <select
                                value={editingId === category.id 
                                    ? String(editCategoryIsActive) 
                                    : String(category.is_active)
                                }
                                disabled={editingId !== category.id}
                                onChange={(e) => 
                                    setEditCategoryIsActive(
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
                                        startEditing(category)
                                    } }>
                                    編集
                                </button>
                                <button 
                                    type="button"
                                    disabled={editingId !== category.id}
                                    onClick={() =>{
                                        editCategorySubmit()
                                    }}>
                                    変更
                                </button>
                            </td>
                        </tr>
                    )
                    })}
                </tbody>
            </table>
        </div>

    )
    
}
export default AdminCategories;
