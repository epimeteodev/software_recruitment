import { useState } from 'react';

/*
function useLocalStorage(key, initial_value: any) {
  localStorage.setItem(key, JSON.stringify(initial_value))
  let push = (e: any) => {
    let v = JSON.parse(localStorage.getItem(key) | "[]");
    v.push(e);
    localStorage.setItem(key, JSON.stringify(v));
  } 
}
*/

interface TODO {
  id: string,
  text: string,
  done: boolean,
}

function App() {
  const [list, setList] = useState<TODO[]>([]);

  function push(t: string) {
    if (t != "") {
      let e: TODO = {
        id: crypto.randomUUID(),
        text: t,
        done: false,
      };  
      setList([...list, e]);
    }
  };

  function toggle(id: string) {
    setList(list.map((e: TODO) => {
      if (e.id == id) {
        e.done = !e.done;
      }
      return e;
    }));
  }

  function remove(id: string) { 
    setList(list.filter((e: TODO) => e.id != id));
  }

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-gray-100 font-mono">
      
      <div
        className="text-blue-500 font-bold text-4xl m-10"
      >What to do?</div>

      <div className="w-xl">
        <TextInputBar onEnter={push}/>
        
        {list.map((todo) =>
          <TodoItem
            key={todo.id} 
            text={todo.text} 
            checked={false}
            onToggle={() => toggle(todo.id)}  
            onRemove={() => remove(todo.id)}
          />
        )}
      </div>

    </div>
  );
}

export default App;

interface ClickButtonArgs {
  onClick: () => void,
  color: string,
  image_path: string,
}
function ClickButton({ color, image_path, onClick }: ClickButtonArgs) {
  return (
    <div 
    onClick={onClick}
    className={`
      ${color}
      bg-white active:bg-current
      ring-2 ring-current
      size-10 rounded-full
      flex items-center justify-center
    `}>
      <div className={`
        size-10 bg-current active:bg-white
        [mask-image:url(${image_path})]
        [mask-size:60%] [mask-repeat:no-repeat] [mask-position:center]
      `}
      style={{ maskImage: `url(${image_path})` }}>
      </div>
    </div>
  );
}

function AddButton({ onClick }: {onClick: () => void}) {
  return (
    <ClickButton
      color="text-blue-500"
      image_path="/img/plus.svg"
      onClick={onClick}
    />
  );
}

interface CheckButtonArgs {
  checked: boolean,
  onToggle: () => void,
}
function CheckButton({ checked, onToggle }: CheckButtonArgs) {
  const [selected, setSelection] = useState(checked);

  let check;
  if (selected) {
    check = (
      <img
        className="invert dark:invert-100"
        src="../img/check.svg"
      />
    );
  }

  return (
    <div
      className={`
        text-black
        ${selected ? "bg-current" : ""}
        size-10 shrink-0 m-2 p-2 rounded-full 
        ring-2 ring-current
        flex items-center justify-center
      `}
      onClick={() => {
        onToggle();
        setSelection(!selected);
      }}
    >
      {check}
    </div>
  );
}

function Bin({ onClick=(() => {}) }: {onClick: () => void}) {
  return (
    <ClickButton
      color="text-red-900"
      image_path="/img/trash.svg"
      onClick={onClick}
    />
  );
}

interface TodoItemArgs {
  text: string,
  checked: boolean,
  onToggle: () => void,
  onRemove: () => void,
}

function TodoItem({ text, checked, onToggle, onRemove }: TodoItemArgs) {
  const [striked, setStrike] = useState(checked);

  return (
    <div className="flex flex-row items-center justify-center m-5">
      
      <CheckButton checked={checked} onToggle={() => {onToggle(); setStrike(!striked);}}/>
      
      <div className={`
        ${striked ? "line-through" : ""}
        m-2 ml-10 pr-10 mr-auto break-all
      `}>
        {text}
      </div>

      <div className={striked ? "" : "hidden"}>
        <Bin onClick={onRemove}/>
      </div>

    </div>
  );
}

function TextInputBar({ onEnter }: {onEnter: (text: string) => void}) {
  const [text, setText] = useState("");

  return (
    <div className="fixed left-0 right-0 bottom-0 m-5 md:static">
      <div className="
        flex flex-row items-center justify-center
        border-2 border-blue-500 rounded-full
        shadow-xl shadow-blue-500/30
      ">
        <textarea
          placeholder="Your first TODO..."
          value={text}
          onChange={(e) => setText(e.target.value.replace(/\n/g, ""))}
          rows={1}
          onKeyDown={(e) => {
            if (e.key == "Enter") {
              onEnter(text);
              setText("");
            }
          }}
          className="
          min-w-0 flex-1 ml-6
          outline-none whitespace-nowrap resize-none
        ">

        </textarea>

        <div className="m-4">
          <AddButton onClick={() => {
            onEnter(text);
            setText("");
          }}/>
        </div>

      </div>
    </div>
  );
}