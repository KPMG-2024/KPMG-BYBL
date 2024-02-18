import PropTypes from 'prop-types';

const Modal = ({ title, children, modalOpen = false, setModalOpen }) => {
  return (
    <div>
      <input
        value={modalOpen}
        type='checkbox'
        checked={modalOpen}
        onChange={() => setModalOpen(!modalOpen)}
        className='modal-toggle'
      />
      <div className='modal'>
        {/* w는 특정 비율로 만들고, max는 최대, mx auto는 중앙에 배치, my는 위아래로 간격을 준다. */}
        <div className='relative modal-box w-full max-w-5xl h-full mx-auto my-8'>
          <label
            onClick={() => setModalOpen(!modalOpen)}
            className='absolute btn btn-sm btn-circle right-2 top-2'>
            ✕
          </label>
          <h3 className='text-lg font-bold'>{title}</h3>
          <div className='py-4'>{children}</div>
        </div>
      </div>
    </div>
  );
};

export default Modal;

Modal.propTypes = {
  title: PropTypes.string,
  children: PropTypes.node,
  modalOpen: PropTypes.bool.isRequired,
  setModalOpen: PropTypes.func.isRequired,
};
