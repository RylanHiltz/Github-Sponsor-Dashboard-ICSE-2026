// Import Swiper React components
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay } from 'swiper/modules';
import { theme } from 'antd';

// Import styles
import 'swiper/swiper-bundle.css';
import styles from "../pages/leaderboard/Leaderboard.module.css"

import type { LeaderboardStatsData } from '../types/LeaderboardUserModel';


const Carousel = (data: LeaderboardStatsData | null) => {

    if (!data) {
        throw console.error("Data Doesnt Exist!");
    }

    const { token } = theme.useToken();

    return (
        <Swiper
            // Make sure to register the Autoplay module
            modules={[Autoplay]}
            spaceBetween={20}
            slidesPerView={4}
            loop={true} // Enable looping
            speed={10000}
            autoplay={{
                delay: 0,
                disableOnInteraction: false,
                pauseOnMouseEnter: true,
            }}
            // Responsive breakpoints
            breakpoints={{
                '@0.00': { slidesPerView: 1, spaceBetween: 10 },
                '@0.75': { slidesPerView: 2, spaceBetween: 20 },
                '@1.00': { slidesPerView: 3, spaceBetween: 20 },
                '@1.50': { slidesPerView: 4, spaceBetween: 20 },
            }}
        >
            {/* Dynamically create slides from data */}
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Total Users Tracked</h3>
                    <h2 id="total-users-stat">{data.total_users.toLocaleString()}</h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Unique Sponsorships</h3>
                    <h2 id="total-sponsorships-stat">{data.total_sponsorships.toLocaleString()}</h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Top Sponsored</h3>
                    <h2>
                        <span className='flex items-center justify-start gap-2'>
                            <img src={data.top_sponsored.avatar_url} alt={data.top_sponsored.username} className='w-8 h-8 rounded-full' />
                            <p className='pb-1 text-[30px]'>{data.top_sponsored.username}</p>
                        </span>
                    </h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Top Sponsoring</h3>
                    <h2>
                        <span className='flex items-center justify-start gap-2'>
                            <img src={data.top_sponsoring.avatar_url} alt={data.top_sponsoring.username} className='w-8 h-8 rounded-full' />
                            <p className='pb-1 text-[30px]'>{data.top_sponsoring.username}</p>
                        </span>
                    </h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Total Users Tracked</h3>
                    <h2 id="total-users-stat">{data.total_users.toLocaleString()}</h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Unique Sponsorships</h3>
                    <h2 id="total-sponsorships-stat">{data.total_sponsorships.toLocaleString()}</h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Top Sponsored</h3>
                    <h2>
                        <span className='flex items-center justify-start gap-2'>
                            <img src={data.top_sponsored.avatar_url} alt={data.top_sponsored.username} className='w-8 h-8 rounded-full' />
                            <p className='pb-1 text-[30px]'>{data.top_sponsored.username}</p>
                        </span>
                    </h2>
                </div>
            </SwiperSlide>
            <SwiperSlide>
                <div className={`${styles.stats} flex-none`} style={{ backgroundColor: token.cardBg }}>
                    <h3>Top Sponsoring</h3>
                    <h2>
                        <span className='flex items-center justify-start gap-2'>
                            <img src={data.top_sponsoring.avatar_url} alt={data.top_sponsoring.username} className='w-8 h-8 rounded-full' />
                            <p className='pb-1 text-[30px]'>{data.top_sponsoring.username}</p>
                        </span>
                    </h2>
                </div>
            </SwiperSlide>
        </Swiper>
    )
}
export default Carousel

