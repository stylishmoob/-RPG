import { useEffect, useState } from "react";
import { Link,useNavigate } from "react-router-dom";

import type { CategoryDataType} from "../types/api";

import "../styles/category.css";

function Category() {
    const [categoryData,setCategoryData] = useState<CategoryDataType | null>(null);

    const [selectedCategoryId,setSelectedCategoryId] = useState<string>("");

    const navigate = useNavigate();

    const user_categories = categoryData?.user_categories ?? [];

    const master_categories=categoryData?.master_categories ?? [];

    useEffect(() => {
        fetchCategoryData();
    },[navigate]);

    useEffect(() => {
        if(user_categories.length === 0) {
            setSelectedCategoryId("");
            return;
        }

        const selectedExists = master_categories.some(
            (masterCategory) =>
                String(masterCategory.id) === selectedCategoryId
        );

        if(!selectedExists){
            setSelectedCategoryId(String(master_categories[0].id));
        }
    },[master_categories,selectedCategoryId]);

    async function fetchCategoryData(){
        try{
            const response  = await fetch("/api/category");
            if(response.status === 401){
                navigate("/login");
                return;
            }
            if(!response.ok){
                throw new Error("データの取得に失敗しました");
            }
            const data = await response.json();
            setCategoryData(data);
            
        }catch(error){
            console.error(error);
        }
    }

    

    async function deleteCategory(category_id: string){
        try{
            const response = await fetch(`/api/category/${category_id}`,{
                method:"DELETE",
                })
            
                if(!response.ok){
                    console.error("データの送信に失敗しました");
                    return;
                }      
                await fetchCategoryData();
        }catch(error){
            console.error("通信エラー",error);
        }       
    }

    async function addCategory(master_category_id: string){
        try{
            const response = await fetch("/api/category/add",{
                method:"POST",
                headers:{
                    "Content-Type":"application/json",
                },
                body:JSON.stringify({
                    master_category_id: master_category_id,
                })
            })
                if(!response.ok){
                    console.error("データの送信に失敗しました");
                    return;
                }
            }catch(error){
                console.error(error);
            }
        }

    return (
        <div className="page">
            <div className="category-main">
                <h1>カテゴリー管理</h1>
                <div className="category-left">
                    <div className="category-left-inner">
                        <h2>カテゴリー一覧</h2>
                        <div className="category-all">
                            <div className="category-all-inner">
                                <table>
                                    {user_categories.map((category) => (
                                    <tr key={category.id}>
                                        <td>{category.name}</td>
                                        <td>  
                                            <button 
                                                className="delete-button" 
                                                onClick={() => deleteCategory(category.id)}
                                            >
                                                削除
                                            </button>                              
                                        </td>
                                    </tr>
                                    ))}
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                            
                <div className="category-right">
                    <div className="category-right-inner">
                        <h2>カテゴリー追加</h2>
                        <div className="category-add">
                            <div className="category-add-inner">
                                
                                <select 
                                    value={selectedCategoryId}
                                    onChange={(e) => setSelectedCategoryId(e.target.value)}
                                >
                                    {master_categories.map((master_category) =>(
                                        <option 
                                            key={master_category.id}
                                            value={String(master_category.id)}
                                        >
                                            {master_category.name}
                                        </option>
                                    ))}
                                    </select>
                                    <button 
                                        className="add-button" 
                                        disabled={selectedCategoryId === ""}
                                        onClick={() => addCategory(selectedCategoryId)}
                                        >
                                            追加
                                    </button>
                                    
                            </div>
                        </div>
                    </div>
                </div>

                <div className="home">
                    <div className="home-inner">
                        <Link to="/">ホームへ</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Category;