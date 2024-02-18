
const Dashboard = () => {
  return (
    
    // 대시보드 넣기
    <main className='relative flex flex-col w-screen h-screen p-1 overflow-hidden dark:bg-light-grey'>
      <iframe
        title='대시보드'
        src='https://public.tableau.com/views/2_17079191820660/real?:language=en-US&:sid=&:display_count=n&:origin=viz_share_link?:showVizHome=no&:embed=true'
        className='w-full h-full'
      />
    </main>
  );
};

export default Dashboard;
