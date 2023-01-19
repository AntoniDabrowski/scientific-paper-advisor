function sayHello() {
  alert('You clicked me!');
}

const project_button = () => {
  return (
    <button
        className="collapsible"
        onClick={sayHello}>
    Default
    </button>
  );
}

export default project_button